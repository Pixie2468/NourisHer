import os
import sys

import pytest

# ensure src is importable as package
sys.path.insert(0, os.path.abspath("."))


@pytest.mark.asyncio
async def test_health_endpoint(monkeypatch):
    import nourisher.main as main
    import nourisher.api.db as db

    async def fake_startup():
        return None

    monkeypatch.setattr(db, "create_extensions_and_tables", fake_startup)

    from httpx import AsyncClient

    async with AsyncClient(app=main.app, base_url="http://test") as ac:
        resp = await ac.get("/health")
        assert resp.status_code == 200
        assert resp.json() == {"status": "ok"}
