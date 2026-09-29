"""
基础 LLM 调用
"""

import os
from openai import OpenAI, AsyncOpenAI
from dotenv import load_dotenv
import asyncio
from app.agent.tools import get_tool_list
from openai.types.chat import ChatCompletionMessageParam


# 读取配置文件
load_dotenv()

MODEL_NAME = os.environ["LLM_MODEL_NAME"]

_client = None
_async_client = None


def _get_client():
    """ "懒加载 OpenAI 客户端"""
    global _client
    if _client is None:
        _client = OpenAI(
            api_key=os.getenv("LLM_API_KEY"), base_url=os.getenv("LLM_BASE_URL")
        )
    return _client


def _get_async_client():
    """ "懒加载 OpenAI 客户端"""
    global _async_client
    if _async_client is None:
        _async_client = AsyncOpenAI(
            api_key=os.getenv("LLM_API_KEY"), base_url=os.getenv("LLM_BASE_URL")
        )
    return _async_client


def generate(prompt: str, timeout: float = 60, max_tokens: int = 1000):
    """
    接收 Prompt 并生成回答
    timeout 默认 60 秒
    max_tokens 默认 1000
    """
    response = _get_client().chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
        stream=False,
        reasoning_effort="high",
        extra_body={"thinking": {"type": "enabled"}},
        max_tokens=max_tokens,
        timeout=timeout,
        tools=get_tool_list(),
        tool_choice="auto",
    )
    content = getattr(response.choices[0].message, "content", None)
    reasoning_content = getattr(response.choices[0].message, "reasoning_content", None)
    if not content:
        # 如果content为空，则直接回退到 reasoning_content
        content = reasoning_content or ""
    return (content, reasoning_content)


async def generate_stream(
    prompt: list[ChatCompletionMessageParam],
    timeout: float = 120,
    max_tokens: int = 3000,
):
    """
    generate 的异步流式输出版本
    """
    response = await _get_async_client().chat.completions.create(
        model=MODEL_NAME,
        messages=prompt,
        stream=True,
        reasoning_effort="high",
        extra_body={"thinking": {"type": "enabled"}},
        max_tokens=max_tokens,
        timeout=timeout,
        tools=get_tool_list(),
        tool_choice="auto",
    )
    async for chunk in response:
        yield chunk


async def main():
    async for chunk in generate_stream(
        [{"role": "user", "content": "请介绍一下 python"}]
    ):
        print(chunk, end="", flush=True)


if __name__ == "__main__":
    asyncio.run(main())
