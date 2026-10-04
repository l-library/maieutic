from app.agent.llm import LLMClient
from openai.types.chat import ChatCompletionChunk, ChatCompletionMessageParam
from typing import AsyncIterable, Literal
from openai.types.chat.chat_completion_chunk import (
    Choice,
    ChoiceDelta,
    ChoiceDeltaToolCall,
    ChoiceDeltaToolCallFunction,
)
import time

FAKE_ID = "chatcmpl-fake-001"
FAKE_MODEL = "fake-model"

# 与 SDK 字段类型严格对齐的别名。
Role = Literal["developer", "system", "user", "assistant", "tool"]
FinishReason = Literal[
    "stop", "length", "tool_calls", "content_filter", "function_call"
]


class FakeLLM(LLMClient):
    """
    继承自 LLMClient
    可以用于模拟 llm 的回复
    """

    def make_chunk(
        self,
        content: str = "",
        *,
        role: Role | None = None,
        finish_reason: FinishReason | None = None,
        tool_calls: list[ChoiceDeltaToolCall] | None = None,
        index: int = 0,
    ) -> ChatCompletionChunk:
        """
        构造 chunk
        """
        delta = ChoiceDelta(role=role, content=content or None)
        if tool_calls:
            delta = ChoiceDelta(tool_calls=tool_calls)
        return ChatCompletionChunk(
            id=FAKE_ID,
            object="chat.completion.chunk",
            created=int(time.time()),
            model=FAKE_MODEL,
            choices=[Choice(index=index, delta=delta, finish_reason=finish_reason)],
        )

    async def generate_stream(
        self,
        prompt: list[ChatCompletionMessageParam],
        timeout: float = 120,
        max_tokens: int = 3000,
    ) -> AsyncIterable[ChatCompletionChunk]:
        """
        结构和 llm 相同，模拟大模型返回
        """
        yield self.make_chunk(role="assistant")  # 首个 chunk 带 role
        flag = False
        for ch in prompt:
            # 按键判断:历史里出现过工具调用,就不再发起工具调用
            if "tool_calls" in ch:
                flag = True
            yield self.make_chunk(content=f"{ch}")
        # 假如对话中没有调用过工具，调用一次
        for i in '{"question":"hello"}':
            if not flag:
                yield self.make_chunk(
                    content="",
                    tool_calls=[
                        ChoiceDeltaToolCall(
                            index=0,
                            id="call_fake_1",
                            type="function",
                            function=ChoiceDeltaToolCallFunction(
                                name="Web_Search", arguments=i
                            ),
                        )
                    ],
                )
        yield self.make_chunk(finish_reason="stop")
