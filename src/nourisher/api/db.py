import os

from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from nourisher.api.config import settings
from nourisher.ml.models import Base

DATABASE_URL = os.getenv("DATABASE_URL", settings.DATABASE_URL)

engine = create_async_engine(DATABASE_URL, future=True)
AsyncSession = async_sessionmaker(engine, expire_on_commit=False)


async def create_extensions_and_tables() -> None:
    # Create pgvector extension if possible. Use a sync connection via engine.begin()
    async with engine.begin() as conn:
        try:
            await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
        except Exception:
            # extension creation may fail on managed DBs; ignore for now
            pass
        await conn.run_sync(Base.metadata.create_all)
