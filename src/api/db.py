import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import text

from .config import settings


DATABASE_URL = os.getenv("DATABASE_URL", settings.DATABASE_URL)

engine = create_async_engine(DATABASE_URL, future=True)
AsyncSession = async_sessionmaker(engine, expire_on_commit=False)


async def create_extensions_and_tables():
    # Create pgvector extension if possible. Use a sync connection via engine.begin()
    async with engine.begin() as conn:
        # create extension if not exists
        try:
            await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
        except Exception:
            # extension creation may fail on managed DBs; ignore for now
            pass
