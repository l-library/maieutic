from unittest.mock import MagicMock

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.agent import tools
from app.models import Base


@pytest.fixture
def tavily_mock(monkeypatch) -> MagicMock:
    """
    模拟 tavily client ，避免访问真实互联网
    """
    client = MagicMock()
    monkeypatch.setattr(tools, "_get_tavily_client", lambda: client)
    return client


@pytest_asyncio.fixture
async def db_session():
    """
    模拟数据库：内存 sqlite 会话，测试数据不入库
    每个测试独立建表，互不影响
    """
    engine = create_async_engine(
        "sqlite+aiosqlite://",
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    async with session_factory() as session:
        yield session
    await engine.dispose()
