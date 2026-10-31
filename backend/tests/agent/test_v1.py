import asyncio
import json

import pytest
from fake_llm import FakeLLM
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.agent import tools
from app.api.v1.endpoints import conversations
from app.db.engine import get_db
from app.main import app
from app.models import Base


@pytest.fixture
def client(monkeypatch) -> TestClient:
    """
    TestClient + 模拟数据库（内存 sqlite），测试数据不入库
    依赖覆盖 get_db，并用 FakeLLM 替换真实大模型
    """
    engine = create_async_engine(
        "sqlite+aiosqlite://",
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
    )
    asyncio.run(_create_tables(engine))
    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    async def override_get_db():
        async with session_factory() as session:
            yield session

    monkeypatch.setattr(conversations, "_get_llm_client", lambda: FakeLLM())
    monkeypatch.setitem(tools.REGISTER, "web_search", lambda question: "SEARCH_RESULT")
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.pop(get_db, None)
    asyncio.run(engine.dispose())


async def _create_tables(engine):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


def test_create_and_get_conversation(client):
    """创建对话返回 id，查询该 id 返回对话历史"""
    response = client.get("/api/v1/conversation/create")
    assert response.status_code == 200
    conversation_id = response.json()
    assert isinstance(conversation_id, int)

    response = client.get(f"/api/v1/conversation/get/{conversation_id}")
    assert response.status_code == 200
    assert response.json() == []


def test_chat_persists_messages(client):
    """对话接口走完整 agent 循环，新消息写入模拟数据库"""
    conversation_id = client.get("/api/v1/conversation/create").json()

    response = client.post(
        f"/api/v1/conversation/chat/{conversation_id}", json={"message": "TEST"}
    )
    assert response.status_code == 200
    events = [
        json.loads(line.removeprefix("data: "))
        for line in response.text.splitlines()
        if line.startswith("data: ")
    ]
    assert any(e["type"] == "tool_calls" for e in events)
    assert events[-1]["type"] == "assistant"

    response = client.get(f"/api/v1/conversation/get/{conversation_id}")
    roles = [m["role"] for m in response.json()]
    assert roles == ["user", "assistant", "tool", "assistant"]


def test_conversations_are_isolated(client):
    """不同对话各自维护历史；最近一条空对话会被复用"""
    first = client.get("/api/v1/conversation/create").json()

    # 最近对话仍为空，再次创建复用同一条
    assert client.get("/api/v1/conversation/create").json() == first

    client.post(f"/api/v1/conversation/chat/{first}", json={"message": "TEST"})

    # 最近对话已有消息，新建一条
    second = client.get("/api/v1/conversation/create").json()
    assert second != first
    assert client.get(f"/api/v1/conversation/get/{second}").json() == []

    assert [
        m["role"] for m in client.get(f"/api/v1/conversation/get/{first}").json()
    ] == [
        "user",
        "assistant",
        "tool",
        "assistant",
    ]
