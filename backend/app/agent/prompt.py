"""
读取提示词，注入工具提示
"""

from pathlib import Path
from functools import lru_cache
import platform

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
# 工作环境相关信息：
操作系统：{self.os_env}
所在目录：'/home/liborui/Documents/workspace/'
            """
        return sys + soul
