"""
提供给 agent 的可调用工具
"""

from os import getenv
from tavily import TavilyClient
from dotenv import load_dotenv

load_dotenv()

_tavily_client = TavilyClient(api_key=getenv("TAVILY_API_KEY"))


def ask_question(qustion: str):
    print("tool call: ask")
    result = input(qustion + "\n")
    return result


def web_search(qustion: str):
    """
    通过搜索引擎搜索
    """
    response = _tavily_client.search(qustion)
    print(response)
    return response


def web_extract(urls: list):
    """
    通过 URLs 提取其原始内容
    """
    response = _tavily_client.extract(urls=urls, include_images=False)
    return response["results"]


if __name__ == "__main__":
    print(web_extract(["https://l-library.xyz"]))
