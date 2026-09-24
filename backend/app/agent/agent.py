"""
Agent 主循环
"""

from openai.types.chat import ChatCompletionMessageParam
from app.agent.prompt import Prompt
from app.agent import llm
import re
from app.agent import tools


class agent:
    def __init__(self) -> None:
        self.prompt = Prompt()
        self.messages: list[ChatCompletionMessageParam] = [
            {"role": "system", "content": self.prompt.get_sys_prompt()}
        ]

    async def core_loop(self, user_message: str, max_loop: int = 10):
        """
        agent 核心循环
        """
        message: list[ChatCompletionMessageParam] = [
            {"role": "user", "content": "<question>" + user_message + "</question>"},
        ]
        self.messages += message
        loop = 0
        parts: list[str] = []
        while loop < max_loop:
            async for piece in llm.generate_stream(self.messages):
                parts.append(piece)
            reply = "".join(parts)
            self.messages.append({"role": "assistant", "content": reply})
            res = self.handle_reply(reply)
            if res:
                break
            input("continue?")
            loop += 1
        return "".join(parts)

    def handle_reply(self, reply: str) -> bool:
        """
        处理 LLM 返回的消息
        返回值：bool，表示是否终止循环
        """
        thought_match = re.search(r"<thought>(.*?)</thought>", reply, re.DOTALL)
        if thought_match:
            print(f"Thought: \n{thought_match.group(1)}\n")
        final_match = re.search(r"<final_answer>(.*?)</final_answer>", reply, re.DOTALL)
        if final_match:
            print(f"\nFinal: {final_match.group(1)}\n")
            return True
        action_match = re.search(r"<action>(.*?)</action>", reply, re.DOTALL)
        if action_match:
            code = "tools." + action_match.group(1)
            be_agreed = input(f"\nAction: {code} Y/n?")
            if be_agreed != "Y":
                self.messages.append(
                    {
                        "role": "user",
                        "content": f"<observation> {code} was aborted by user </observation>",
                    }
                )
            else:
                tool_res = eval(code)
                print(f"\nTool sucess: {tool_res}\n")
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
        return False
