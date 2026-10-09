"""
基础 LLM 调用
"""

import os
from collections.abc import AsyncIterable
from typing import Any, Protocol

from dotenv import load_dotenv
from openai import AsyncOpenAI, OpenAI
from openai.types.chat import ChatCompletionChunk, ChatCompletionMessageParam

from app.agent.tools import get_tool_list

# 读取配置文件
load_dotenv()

MODEL_NAME = os.environ["LLM_MODEL_NAME"]


# 用于依赖注入
class LLMClient(Protocol):
    def generate_stream(
        self,
        prompt: list[ChatCompletionMessageParam],
        timeout: float = 120,
        max_tokens: int = 3000,
    ) -> AsyncIterable[ChatCompletionChunk]: ...


class LLM(LLMClient):
    client: Any
    async_client: Any

    def __init__(self) -> None:
        self.client = None
        self.async_client = None

    def _get_client(self):
        """ "懒加载 OpenAI 客户端"""
        if self.client is None:
            self.client = OpenAI(
                api_key=os.getenv("LLM_API_KEY"), base_url=os.getenv("LLM_BASE_URL")
            )
        return self.client

    def _get_async_client(self):
        """ "懒加载 OpenAI 客户端"""
        if self.async_client is None:
            self.async_client = AsyncOpenAI(
                api_key=os.getenv("LLM_API_KEY"), base_url=os.getenv("LLM_BASE_URL")
            )
        return self.async_client

    def generate(self, prompt: str, timeout: float = 60, max_tokens: int = 1000):
        """
        接收 Prompt 并生成回答
        timeout 默认 60 秒
        max_tokens 默认 1000
        """
        response = self._get_client().chat.completions.create(
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
        reasoning_content = getattr(
            response.choices[0].message, "reasoning_content", None
        )
        if not content:
            # 如果content为空，则直接回退到 reasoning_content
            content = reasoning_content or ""
        return content, reasoning_content

    async def generate_stream(
        self,
        prompt: list[ChatCompletionMessageParam],
        timeout: float = 120,
        max_tokens: int = 3000,
    ) -> AsyncIterable[ChatCompletionChunk]:
        """
        generate 的异步流式输出版本
        """
        response = await self._get_async_client().chat.completions.create(
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
