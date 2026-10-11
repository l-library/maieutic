import json

import pytest
from fake_llm import FakeLLM

from app.agent import tools
from app.agent.agent import core_loop
from app.services import conversation as conversation_service

ALLOWED_KEYS = {"type", "content"}


async def run_core_loop(db_session, conversation_id, history, user_message):
    """用 FakeLLM 跑一次 core_loop，收集产出的 chunk"""
    return [
        chunk
        async for chunk in core_loop(
            history=history,
            user_message=user_message,
            llm=FakeLLM(),
            db_session=db_session,
            conversation_id=conversation_id,
        )
    ]


@pytest.mark.asyncio
async def test_core_loop_full(db_session, monkeypatch):
    """完整循环: 工具调用 -> 工具结果 -> 最终回复，新消息写入模拟数据库"""
    monkeypatch.setitem(tools.REGISTER, "web_search", lambda question: "SEARCH_RESULT")
    conv_id = await conversation_service.create_conversation("test", db_session)
    history = await conversation_service.get_conversation(db_session, conv_id)

    chunks = await run_core_loop(db_session, conv_id, history, "TEST")

    # 第一轮有工具调用,最后是正文回复
    assert any(c["type"] == "tool_calls" for c in chunks)
    assert chunks[-1]["type"] == "assistant"
    assert all(set(c.keys()) == ALLOWED_KEYS for c in chunks)

    # 落库消息历史: user -> assistant(tool_calls) -> tool -> assistant
    stored = await conversation_service.get_conversation(db_session, conv_id)
    roles = [m["role"] for m in stored]
    assert roles == ["user", "assistant", "tool", "assistant"]
    tool_call = stored[1]["tool_calls"][0]
    assert tool_call["function"]["name"] == "Web_Search"
    assert json.loads(tool_call["function"]["arguments"]) == {"question": "hello"}
    assert stored[2] == {
        "role": "tool",
        "content": "SEARCH_RESULT",
        "tool_call_id": "call_fake_1",
    }


@pytest.mark.asyncio
async def test_core_loop_interrupt_and_resume(db_session, monkeypatch):
    """工具挂起等待用户输入,用户回复后以 tool 消息恢复，历史完整落库"""
    iv = tools.Interrupt(kind="ask_user", payload="hello")
    monkeypatch.setitem(
        tools.REGISTER, "web_search", lambda question: (_ for _ in ()).throw(iv)
    )
    conv_id = await conversation_service.create_conversation("test", db_session)

    # 第一轮: 抛 Interrupt 后循环挂起,assistant(tool_calls) 后没有 tool 结果
    history = await conversation_service.get_conversation(db_session, conv_id)
    await run_core_loop(db_session, conv_id, history, "TEST")
    stored = await conversation_service.get_conversation(db_session, conv_id)
    assert [m["role"] for m in stored] == ["user", "assistant"]
    assert stored[-1]["tool_calls"][0]["id"] == "call_fake_1"

    # 第二轮: 用户回复作为 tool 消息补上,循环正常结束
    chunks = await run_core_loop(db_session, conv_id, stored, "USER_REPLY")
    stored = await conversation_service.get_conversation(db_session, conv_id)
    assert stored[2] == {
        "role": "tool",
        "content": "USER_REPLY",
        "tool_call_id": "call_fake_1",
    }
    assert [m["role"] for m in stored] == ["user", "assistant", "tool", "assistant"]
    assert all(set(c.keys()) == ALLOWED_KEYS for c in chunks)


@pytest.mark.asyncio
async def test_core_loop_appends_history(db_session, monkeypatch):
    """已有对话历史只追加新消息，不覆盖旧内容"""
    monkeypatch.setitem(tools.REGISTER, "web_search", lambda question: "SEARCH_RESULT")
    conv_id = await conversation_service.create_conversation("test", db_session)
    await conversation_service.append_new_messages(
        db_session,
        conv_id,
        [{"role": "user", "content": "OLD"}, {"role": "assistant", "content": "OLD"}],
    )

    history = await conversation_service.get_conversation(db_session, conv_id)
    await run_core_loop(db_session, conv_id, history, "TEST")

    stored = await conversation_service.get_conversation(db_session, conv_id)
    assert [m["content"] for m in stored[:2]] == ["OLD", "OLD"]
    assert [m["role"] for m in stored[2:]] == ["user", "assistant", "tool", "assistant"]
