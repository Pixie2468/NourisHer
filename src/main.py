from fastapi import FastAPI

from api.db import create_extensions_and_tables
from api.routes.stream import router as stream_router

app = FastAPI(title="NourisHer API")


@app.on_event("startup")
async def on_startup() -> None:
    await create_extensions_and_tables()


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}


app.include_router(stream_router)
