import json
import logging
from typing import AsyncGenerator, List

from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import StreamingResponse
from starlette.concurrency import iterate_in_threadpool, run_in_threadpool

from api.config import settings
from api.db import AsyncSession
from api.ml_model import generate, stream_generate
from ml.models.models import Record
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
                        out = await run_in_threadpool(
                            generate, payload.get("prompt") or json.dumps(payload)
                        )
                    except Exception:
                        logger.exception("model generation failed")
                        out = {"error": "generation_failed"}

                    batch.append(
                        {
                            "input": payload,
                            "output": out,
                            "meta": None,
                        }
                    )

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
        raise HTTPException(
            status_code=415, detail="Unsupported content-type. Use application/x-ndjson"
        )


@router.post("/stream/sse")
async def stream_sse(request: Request):
    """Accept a JSON body and stream model output via SSE."""

    async def event_generator() -> AsyncGenerator[str, None]:
        try:
            payload = await request.json()
        except Exception:
            payload = {}
        prompt = payload.get("prompt") or json.dumps(payload)
        try:
            async for chunk in iterate_in_threadpool(stream_generate(prompt)):
                data = json.dumps({"text": chunk})
                yield f"data: {data}\n\n"
        except Exception:
            logger.exception("model generation failed")
            data = json.dumps({"error": "generation_failed"})
            yield f"data: {data}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")
