import os
import sys

import pytest

# ensure src is importable as package
sys.path.insert(0, os.path.abspath("."))


@pytest.mark.asyncio
async def test_sse_stream_endpoint(monkeypatch):
    import nourisher.api.routes.stream as routes

    def fake_stream_generate(prompt, max_new_tokens=128, **kwargs):
        del max_new_tokens
        yield "pcos"
        yield ": "
        yield "1"

    monkeypatch.setattr(routes, "stream_generate", fake_stream_generate)

    import nourisher.main as main
    import nourisher.api.db as db

    async def fake_startup():
        return None

    monkeypatch.setattr(db, "create_extensions_and_tables", fake_startup)

    from httpx import AsyncClient

    async with AsyncClient(app=main.app, base_url="http://test") as ac:
        resp = await ac.post("/stream/sse", json={"prompt": "test"})
        assert resp.status_code == 200
        body = resp.text
        assert "data:" in body
        assert "pcos" in body
