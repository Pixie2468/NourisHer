import os
import sys

import pytest

# ensure src is importable as package
sys.path.insert(0, os.path.abspath("."))


class DummyConn:
    def __init__(self):
        self.executed = []
        self.synced = False

    async def execute(self, stmt):
        self.executed.append(str(stmt))

    async def run_sync(self, fn):
        self.synced = True
        fn(None)


class DummyBegin:
    def __init__(self, conn):
        self.conn = conn

    async def __aenter__(self):
        return self.conn

    async def __aexit__(self, exc_type, exc, tb):
        del exc_type
        del exc
        del tb
        return False


class DummyEngine:
    def __init__(self, conn):
        self._conn = conn

    def begin(self):
        return DummyBegin(self._conn)


@pytest.mark.asyncio
async def test_create_extensions_and_tables(monkeypatch):
    import nourisher.api.db as db

    conn = DummyConn()
    monkeypatch.setattr(db, "engine", DummyEngine(conn))

    class DummyBase:
        class metadata:
            @staticmethod
            def create_all(_):
                return None

    monkeypatch.setattr(db, "Base", DummyBase)

    await db.create_extensions_and_tables()
    assert conn.synced is True
    assert any("CREATE EXTENSION" in stmt for stmt in conn.executed)
