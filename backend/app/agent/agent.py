"""
Agent 主循环
"""

import json
from collections.abc import AsyncGenerator, Mapping
from typing import Any

from loguru import logger
from openai.types.chat import (
    ChatCompletionAssistantMessageParam,
    ChatCompletionMessageParam,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.agent import tools
from app.agent.llm import LLMClient
from app.agent.prompt import Prompt
from app.services import conversation as conversation_db

async def core_loop(
    history: list[ChatCompletionMessageParam],
    user_message: str,
    llm: LLMClient,
    db_session: AsyncSession,
    conversation_id: int,
    max_loop: int = 10,
) -> AsyncGenerator[dict[str, Any], None]:
    """
    agent 核心循环
    """
    # 先判断输入的消息是新的对话还是上一轮消息调用的结果
    message: list[ChatCompletionMessageParam] = [
        {"role": "user", "content": user_message}
    ]
    if history:
        last_message: Mapping[str, Any] = history[-1]  # 异构历史，按普通映射读取
        if "tool_calls" in last_message:
            message = [
                {
                    "role": "tool",
                    "content": user_message,
                    "tool_call_id": last_message["tool_calls"][0]["id"],
                },
            ]

    new_context: list[ChatCompletionMessageParam] = (
        message  # 用于存放最后写入数据库的所有新内容
    )

    # 传给 llm 的上下文
    _prompt = Prompt()
    _sys_prompt: list[ChatCompletionMessageParam] = [
        {"role": "system", "content": _prompt.get_sys_prompt()}
    ]

    loop = 0
    flag = True
    while (loop < max_loop) and flag:
        loop += 1
        tool_calls_acc: dict[
            Any, Any
        ] = {}  # key: index value: {"id","name","arguments"}
        content_parts = []
        # 传给 llm 的上下文增长
        _context: list[ChatCompletionMessageParam] = _sys_prompt + history + new_context
        # 调用 LLM 获取 chunk
        async for chunk in llm.generate_stream(_context):
            if not chunk.choices:
                continue
            choice = chunk.choices[0]
            delta = choice.delta

            # 思考内容
            reasoning_content = getattr(delta, "reasoning_content", None)
            if reasoning_content:
                yield {"type": "reasoning", "content": reasoning_content}

            # 正文
            content = getattr(delta, "content", None)
            if content:
                content_parts.append(content)
                yield {"type": "assistant", "content": content}

            # 工具调用
            tool_calls = delta.tool_calls
            if tool_calls:
                for tc in tool_calls or []:
                    acc = tool_calls_acc.setdefault(
                        tc.index, {"id": "", "name": "", "arguments": ""}
                    )  # acc 作为草稿
                    if tc.id:
                        acc["id"] = tc.id  # 只在第一个分片出现
                    if tc.function and tc.function.name:
                        acc["name"] = tc.function.name  # 只在第一个分片出现
                    if tc.function and tc.function.arguments:
                        acc["arguments"] += tc.function.arguments  # 增量拼接

        new_message: ChatCompletionAssistantMessageParam = {
            "role": "assistant",
            "content": "".join(content_parts) or None,
        }  # 一条新消息
        logger.info(f"Assistant message: \n{new_message}\n")
        # 是否有工具调用
        if tool_calls_acc:
            # 先构建完整消息
            new_message["tool_calls"] = [
                {
                    "id": slot["id"],
                    "type": "function",
                    "function": {
                        "name": slot["name"],
                        "arguments": slot["arguments"],
                    },
                }
                for _, slot in sorted(tool_calls_acc.items())
            ]
            new_context.append(new_message)
            for slot in tool_calls_acc.values():  # 取出所有工具调用
                name = slot["name"].lower()
                args = json.loads(slot["arguments"]) if slot["arguments"] else {}
                logger.info(f"tool_call: {name}, {args}")
                yield {"type": "tool_calls", "content": f"{name}({args})"}
                try:
                    tool_res = tools.REGISTER[name](**args)
                    logger.info(f"tool_res:{tool_res}")
                    new_context.append(
                        {
                            "role": "tool",
                            "content": str(tool_res),
                            "tool_call_id": slot["id"],
                        }
                    )
                    yield {"type": "tool", "content": tool_res}
                except tools.Interrupt:
                    logger.info(f"Waiting for user input, id: {slot['id']}")
                    flag = False
                except Exception as e:  # noqa: BLE001
                    new_context.append(
                        {
                            "role": "tool",
                            "content": f"Error: {e!s}",
                            "tool_call_id": slot["id"],
                        }
                    )
                    logger.info(f"TOOL_CALL_ERROR: {e!s}")
        else:
            new_context.append(new_message)
            flag = False

    await conversation_db.append_new_messages(db_session, conversation_id, new_context)
