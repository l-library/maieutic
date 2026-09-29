"""
Agent 主循环
"""

from loguru import logger
from openai.types.chat import ChatCompletionMessageParam
from tavily.utils import json
from app.agent.prompt import Prompt
from app.agent import llm
from app.agent import tools


class agent:
    def __init__(self) -> None:
        self.prompt = Prompt()
        self.messages: list[ChatCompletionMessageParam] = [
            {"role": "system", "content": self.prompt.get_sys_prompt()}
        ]
        self.pending = None
        self.tool_call_id = ""

    async def core_loop(self, user_message: str, max_loop: int = 10):
        """
        agent 核心循环
        """
        # 先判断输入的消息是新的对话还是上一轮消息调用的结果
        if self.pending:
            message: list[ChatCompletionMessageParam] = [
                {
                    "role": "tool",
                    "content": user_message,
                    "tool_call_id": self.tool_call_id,
                },
            ]
            self.pending = None
        else:
            message: list[ChatCompletionMessageParam] = [
                {"role": "user", "content": user_message}
            ]

        self.messages += message

        loop = 0
        flag = True
        while (loop < max_loop) and flag:
            loop += 1
            tool_calls_acc = {}  # key: index value: {"id","name","arguments"}
            content_parts = []
            # 调用 LLM 获取 chunk
            async for chunk in llm.generate_stream(self.messages):
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
                    yield {"type": "tool_calls", "content": tool_calls}
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

            new_message: ChatCompletionMessageParam = {
                "role": "assistant",
                "content": "".join(content_parts) or None,
            }
            logger.info(f"Assistant message: \n------{new_message}\n------")
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
                self.messages.append(new_message)
                for _, slot in tool_calls_acc.items():  # 取出所有工具调用
                    name = slot["name"].lower()
                    args = json.loads(slot["arguments"]) if slot["arguments"] else {}
                    logger.info(f"tool_call: {name}, {args}")
                    # TODO: 错误处理
                    try:
                        tool_res = tools.REGISTER[name](**args)
                        logger.info(f"tool_res:{tool_res}")
                        self.messages.append(
                            {
                                "role": "tool",
                                "content": str(tool_res),
                                "tool_call_id": slot["id"],
                            }
                        )
                    except tools.Interrupt as iv:  # interrupt Vector
                        logger.info(f"Waitting for user input, id: {slot['id']}")
                        self.pending = iv
                        self.tool_call_id = slot["id"]
                        flag = False
            else:
                self.messages.append(new_message)
                flag = False
