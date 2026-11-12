"""
提供给 agent 的可调用工具
"""

import subprocess
from collections.abc import Callable
from os import getenv
from pathlib import Path

from dotenv import load_dotenv
from openai import BaseModel, pydantic_function_tool
from tavily import TavilyClient

load_dotenv()

_tavily_client = None


def _get_tavily_client():
    global _tavily_client
    if _tavily_client is None:
        _tavily_client = TavilyClient(api_key=getenv("TAVILY_API_KEY"))
    return _tavily_client


class Interrupt(Exception):
    """需要外部输入而挂起循环"""

    def __init__(self, kind: str, payload: str):
        self.kind, self.payload = kind, payload


CLASS_REGISTER: dict[str, type[BaseModel]] = {}
REGISTER: dict[str, Callable] = {}


# tool 注册器
def tool(cl: type[BaseModel]):  # 表示类本身而非实例
    CLASS_REGISTER[cl.__name__] = cl
    return cl


# fun 注册器
def fun(fn: Callable):
    REGISTER[fn.__name__] = fn
    return fn


# 定义数据模型描述工具参数
@tool
class Ask_Question(BaseModel):
    """
    向用户问问题
    """

    question: str


@tool
class Web_Search(BaseModel):
    """
    通过搜索引擎搜索
    """

    question: str


@tool
class Web_Extract(BaseModel):
    """
    解析 urls ，返回网页的原始内容，可以输入多个
    """

    urls: list[str]


@tool
class Read(BaseModel):
    """
    阅读指定文件的内容
    """

    path: str


@tool
class Bash(BaseModel):
    """
    执行 Bash 命令
    """

    command: str


def get_tool_list():
    """
    获取 openai 格式工具列表
    """
    return [pydantic_function_tool(m) for m in CLASS_REGISTER.values()]


@fun
def ask_question(question: str):
    """
    向用户问问题，用户的回复将作为下一步的输入
    """
    raise (Interrupt(kind="ask_user", payload=question))


@fun
def web_search(question: str) -> str:
    """
    通过搜索引擎搜索，用户的回复将作为下一步的输入
    """
    response = _get_tavily_client().search(question)
    return str(response)


@fun
def web_extract(urls: list) -> str:
    """
    解析 urls ，返回网页的原始内容，可以输入多个
    """
    response = _get_tavily_client().extract(urls=urls, include_images=False)
    return response["results"]


@fun
def read(path: str) -> str:
    """
    阅读指定文件的内容
    """
    _path = Path(path)
    if _path.is_file():
        with _path.open(encoding="utf-8-sig") as f:
            content = f.read()
        return content
    else:
        raise OSError(f"Path '{path}' is not a file")


@fun
def bash(command: str) -> str:
    """
    执行 Bash 命令
    """

    res = subprocess.getstatusoutput(command)

    return f"Return_code:{res[0]}\nstdout:{res[1]}"
