"""
ORM 连接初始化
"""

import os
from pathlib import Path
from typing import AsyncIterator

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

load_dotenv()

_database_url = ""


def get_database_url():
    global _database_url
    if _database_url == "":
        _database_url_relative = os.getenv("DATABASE_URL_RELATIVE")
        _base_dir = Path(__file__).resolve().parent.parent.parent  # 指向 backend/
        _database_url = f"sqlite+aiosqlite:///{_base_dir}/{_database_url_relative}"
    return _database_url


engine = create_async_engine(get_database_url())

SessionLocal = async_sessionmaker(engine, autoflush=False, expire_on_commit=False)


async def get_db() -> AsyncIterator[AsyncSession]:
    async with SessionLocal() as session:
        yield session
