"""
Agent 主循环
"""

from openai.types.chat import ChatCompletionMessageParam
from app.agent.prompt import Prompt
from app.agent import llm
import re
from app.agent import tools
import ast


class agent:
    def __init__(self) -> None:
        self.prompt = Prompt()
        self.messages: list[ChatCompletionMessageParam] = [
            {"role": "system", "content": self.prompt.get_sys_prompt()}
        ]
        self.pending = None

    async def core_loop(self, user_message: str, max_loop: int = 10) -> list[dict]:
        """
        agent 核心循环
        """
        # 先判断输入的消息是新的对话还是上一轮消息调用的结果
        xml_block = "question"
        if self.pending:
            xml_block = "observation"
            self.pending = None
        message: list[ChatCompletionMessageParam] = [
            {"role": "user", "content": f"<{xml_block}>{user_message}</{xml_block}>"},
        ]
        self.messages += message
        loop = 0
        res = []
        while loop < max_loop:
            parts: list[str] = []
            async for piece in llm.generate_stream(self.messages):
                parts.append(piece)
            reply = "".join(parts)
            self.messages.append({"role": "assistant", "content": reply})
            res.extend(self.handle_reply(reply))
            if res[-1]["type"] == "final" or self.pending:
                break
        return res

    def handle_reply(self, reply: str) -> list[dict]:
        """
        处理 LLM 返回的消息
        返回值：字典列表
        """
        res: list[dict] = []
        thought_match = re.search(r"<thought>(.*?)</thought>", reply, re.DOTALL)
        if thought_match:
            res.append({"type": "thought", "content": thought_match.group(1)})
        final_match = re.search(r"<final_answer>(.*?)</final_answer>", reply, re.DOTALL)
        if final_match:
            res.append({"type": "final", "content": final_match.group(1)})
        action_match = re.search(r"<action>(.*?)</action>", reply, re.DOTALL)
        if action_match:
            res.append({"type": "action", "content": action_match.group(1)})
            # 解析action
            node = ast.parse(action_match.group(1), mode="eval")
            name = ""
            args = []
            if isinstance(node.body, ast.Call) and isinstance(node.body.func, ast.Name):
                name = node.body.func.id
                args = [ast.literal_eval(arg) for arg in node.body.args]
            # TODO: 调用失败

            # 需要退出循环的场景
            try:
                tool_res = tools.REGISTER[name](*args)
            except tools.Interrupt as iv:  # interrupt Vector
                self.pending = iv
                res.append({"type": iv.kind, "content": iv.payload})
                return res
            res.append({"type": "action_result", "content": tool_res})
            self.messages.append(
                {
                    "role": "user",
                    "content": f"<observation> {tool_res} </observation>",
                }
            )
        else:
            self.messages.append(
                {
                    "role": "user",
                    "content": "<observation> Tool failed: unknow call </observation>",
                }
            )
        return res
