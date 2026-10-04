import json

import pytest

import app.agent.tools as tools
from app.agent.agent import agent
from fake_llm import FakeLLM

ALLOWED_KEYS = {"type", "content"}


def make_agent() -> agent:
    """每个测试用全新的 agent,避免共享对话历史"""
    return agent(FakeLLM())


@pytest.mark.asyncio
async def test_core_loop_full(monkeypatch):
    """完整循环: 工具调用 -> 工具结果 -> 最终回复，使用猴子补丁"""
    monkeypatch.setitem(
        tools.REGISTER, "web_search", lambda question: "SEARCH_RESULT"
    )  # 替换真实搜索工具
    a = make_agent()
    chunks = [chunk async for chunk in a.core_loop("TEST")]

    # 第一轮有工具调用,最后是正文回复
    assert any(c["type"] == "tool_calls" for c in chunks)
    assert chunks[-1]["type"] == "assistant"
    assert all(set(c.keys()) == ALLOWED_KEYS for c in chunks)

    # 消息历史: system -> user -> assistant(tool_calls) -> tool -> assistant
    roles = [m["role"] for m in a.messages]
    assert roles == ["system", "user", "assistant", "tool", "assistant"]
    tool_call = a.messages[2]["tool_calls"][0]
    assert tool_call["function"]["name"] == "Web_Search"
    assert json.loads(tool_call["function"]["arguments"]) == {"question": "hello"}
    assert a.messages[3] == {
        "role": "tool",
        "content": "SEARCH_RESULT",
        "tool_call_id": "call_fake_1",
    }


@pytest.mark.asyncio
async def test_core_loop_interrupt_and_resume(monkeypatch):
    """工具挂起等待用户输入,用户回复后以 tool 消息恢复"""
    iv = tools.Interrupt(kind="ask_user", payload="hello")
    monkeypatch.setitem(
        tools.REGISTER, "web_search", lambda question: (_ for _ in ()).throw(iv)
    )
    a = make_agent()

    # 第一轮: 抛 Interrupt 后循环挂起,assistant(tool_calls) 后没有 tool 结果
    [chunk async for chunk in a.core_loop("TEST")]
    assert a.pending is iv
    assert a.tool_call_id == "call_fake_1"
    assert a.messages[-1]["tool_calls"]
    assert not any(m["role"] == "tool" for m in a.messages)

    # 第二轮: 用户回复作为 tool 消息补上,循环正常结束
    chunks = [chunk async for chunk in a.core_loop("USER_REPLY")]
    assert a.pending is None
    assert a.messages[3] == {
        "role": "tool",
        "content": "USER_REPLY",
        "tool_call_id": "call_fake_1",
    }
    assert a.messages[-1]["role"] == "assistant"
    assert all(set(c.keys()) == ALLOWED_KEYS for c in chunks)
