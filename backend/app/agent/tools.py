"""
提供给 agent 的可调用工具
"""

from os import getenv
from typing import Callable
from tavily import TavilyClient
from dotenv import load_dotenv

load_dotenv()

_tavily_client = TavilyClient(api_key=getenv("TAVILY_API_KEY"))


class Interrupt(Exception):
    """需要外部输入而挂起循环"""

    def __init__(self, kind: str, payload: str):
        self.kind, self.payload = kind, payload


REGISTER: dict[str, Callable] = {}


# tool 注册器
def tool(fn: Callable):
    REGISTER[fn.__name__] = fn
    return fn


def get_tool_inf() -> str:
    inf: str = ""
    for i, j in REGISTER.items():
        inf += f"\n---\n{i}\n{j.__doc__}\n---"
    return inf


@tool
def ask_question(question: str):
    """
    简介：向用户问问题，用户的回复将作为下一步的输入
    示例：<action>ask_question("如何称呼你")</action>
    """
    raise (Interrupt(kind="ask_user", payload=question))


@tool
def web_search(question: str) -> str:
    """
    简介：通过搜索引擎搜索，用户的回复将作为下一步的输入
    示例：<action>web_search("埃菲尔铁塔有多高")</action>
    """
    response = _tavily_client.search(question)
    return str(response)


@tool
def web_extract(urls: list) -> str:
    """
    简介：解析 urls ，返回网页的原始内容，可以输入多个
    示例： <action>web_extract(["https://github.com","https://baidu.com"])</action>
    """
    response = _tavily_client.extract(urls=urls, include_images=False)
    return response["results"]
