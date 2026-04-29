import json
import logging
from typing import List

from fastapi import APIRouter, Request, Depends, HTTPException
from starlette.concurrency import run_in_threadpool

from ..config import settings
from ..db import AsyncSession
from ..ml_model import generate
from ..models import Record
from sqlalchemy import insert

router = APIRouter()
logger = logging.getLogger(__name__)


async def _flush_batch(session, batch: List[dict]):
    if not batch:
        return
    stmt = insert(Record).values(batch)
    await session.execute(stmt)
    await session.commit()


@router.post("/stream")
async def stream(request: Request):
    """Accept a NDJSON stream of JSON objects in request body.

    Each line is parsed as JSON, passed to the model for generation, and stored
    in the records table along with the model output.
    """
    if request.headers.get("content-type", "").startswith("application/x-ndjson"):
        session = AsyncSession()
        batch = []
        try:
            async for chunk in request.stream():
                try:
                    text = chunk.decode()
                except Exception:
                    text = chunk.decode(errors="ignore")
                lines = text.splitlines()
                for line in lines:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        payload = json.loads(line)
                    except Exception:
                        logger.exception("failed parse line: %s", line)
                        continue
                    # run generation in threadpool to avoid blocking
                    try:
                        out = await run_in_threadpool(generate, payload.get("prompt") or json.dumps(payload))
                    except Exception:
                        logger.exception("model generation failed")
                        out = {"error": "generation_failed"}

                    batch.append({
                        "input": payload,
                        "output": out,
                    })

                    if len(batch) >= settings.BATCH_SIZE:
                        await _flush_batch(session, batch)
                        batch = []

            # final flush
            if batch:
                await _flush_batch(session, batch)
        finally:
            await session.close()

        return {"status": "ok"}
    else:
        raise HTTPException(status_code=415, detail="Unsupported content-type. Use application/x-ndjson")
