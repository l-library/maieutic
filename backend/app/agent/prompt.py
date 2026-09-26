"""
读取提示词
"""

from pathlib import Path
from functools import lru_cache
import platform
from app.agent.tools import get_tool_inf

PROMPT_DIR = Path(__file__).resolve().parent


class PromptNotFoundError(FileNotFoundError):
    pass


class Prompt:
    def __init__(self) -> None:
        self.os_env = self.get_env()

    def get_env(self):
        self.os_env = platform.system()
        if not self.os_env:
            self.os_env = "UNKNOW"
        return self.os_env

    @lru_cache(maxsize=None)
    def read(self, path: str, mtime: float) -> str:
        return Path(path).read_text(encoding="utf-8")

    def get_sys_prompt(self) -> str:
        path = PROMPT_DIR / "SOUL.md"
        if not path.is_file():
            raise PromptNotFoundError(f"提示词文件不存在: {path}")
        # 获取文件的修改时间，当作参数传给_read
        # 只要不变，_read就会缓存命中，而不读文件；如果没有命中，就说明文件被修改了，自动热重载
        soul = self.read(str(path), path.stat().st_mtime).strip()
        sys = f"""
# agent 工作须知
## 工作环境相关信息：
操作系统：{self.os_env}
所在目录：'/home/liborui/Documents/workspace/'
## 输出要求
你需要将工作分解为多个步骤，每一次输出时，只输出一个步骤。对于每个步骤，首先使用 <thought> 思考要做什么，然后使用可用工具之一决定一个 <action>。接着，你将根据你的行动从环境/工具中收到一个 <observation>。持续这个思考和行动的过程，直到你有足够的信息来提供 <final_answer>。
所有步骤请严格使用以下 XML 标签格式输出，每次只输出一个 XML 块：
- <question> 用户问题
- <thought> 思考
- <action> 采取的工具操作
- <observation> 工具或环境返回的结果
- <final_answer> 最终答案
⸻
例子 1:
<question>埃菲尔铁塔有多高？</question>
<thought>我需要找到埃菲尔铁塔的高度。可以使用搜索工具。</thought>
<action>web_search("埃菲尔铁塔高度")</action>
<observation>埃菲尔铁塔的高度约为330米（包含天线）。</observation>
<thought>搜索结果显示了高度。我已经得到答案了。</thought>
<final_answer>埃菲尔铁塔的高度约为330米。</final_answer>

请严格遵守：
- 你每次回答都必须包括两个标签，第一个是 <thought>，第二个是 <action> 或 <final_answer>
- 输出 <action> 后立即停止生成，等待真实的 <observation>，擅自生成 <observation> 将导致错误

## tools
            """
        return sys + soul + get_tool_inf()
