import os
import sys
import pytest

# ensure src is importable as package
sys.path.insert(0, os.path.abspath("."))


class DummySession:
    def __init__(self, *args, **kwargs):
        pass

    async def execute(self, *args, **kwargs):
        return None

    async def commit(self):
        return None

    async def close(self):
        return None


@pytest.mark.asyncio
async def test_stream_endpoint(monkeypatch):
    # Patch AsyncSession to avoid requiring a real DB during unit test
    import nourisher.api.db as db

    monkeypatch.setattr(db, "AsyncSession", DummySession)

    # Patch the model generate function to be deterministic
    import nourisher.api.ml_model as ml_model

    def fake_generate(prompt, max_new_tokens=128, **kwargs):
        return {"text": f"pred:{prompt}"}

    monkeypatch.setattr(ml_model, "generate", fake_generate)

    # Capture batches instead of hitting a real DB
    import nourisher.api.routes.stream as routes

    captured = []

    async def fake_flush(session, batch):
        captured.append(batch)

    monkeypatch.setattr(routes, "_flush_batch", fake_flush)

    # Import app after monkeypatching to avoid startup DB work
    import nourisher.main as main
    import nourisher.api.db as db

    async def fake_startup():
        return None

    monkeypatch.setattr(db, "create_extensions_and_tables", fake_startup)

    app = main.app
    from httpx import AsyncClient

    ndjson = '{"prompt":"hello"}\n{"prompt":"bye"}\n'

    async with AsyncClient(app=app, base_url="http://test") as ac:
        resp = await ac.post("/stream", data=ndjson, headers={"content-type": "application/x-ndjson"})
        assert resp.status_code == 200
        assert resp.json() == {"status": "ok"}

    # ensure one batch was flushed and it contains two records
    assert len(captured) == 1
    assert len(captured[0]) == 2
    for item in captured[0]:
        assert "input" in item and "output" in item
