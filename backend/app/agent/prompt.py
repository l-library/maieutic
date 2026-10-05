"""
读取提示词，注入工具提示
"""

import platform
from functools import lru_cache
from pathlib import Path

PROMPT_DIR = Path(__file__).resolve().parent


class PromptNotFoundError(FileNotFoundError):
    pass


@lru_cache
def _read(path: str, mtime: float) -> str:
    return Path(path).read_text(encoding="utf-8")


class Prompt:
    def __init__(self) -> None:
        self.os_env = self.get_env()

    def get_env(self):
        self.os_env = platform.system()
        if not self.os_env:
            self.os_env = "UNKNOW"
        return self.os_env

    def get_sys_prompt(self) -> str:
        path = PROMPT_DIR / "SOUL.md"
        if not path.is_file():
            raise PromptNotFoundError(f"提示词文件不存在: {path}")
        # 获取文件的修改时间，当作参数传给_read
        # 只要不变，_read就会缓存命中，而不读文件；如果没有命中，就说明文件被修改了，自动热重载
        soul = _read(str(path), path.stat().st_mtime).strip()
        sys = f"""
# 工作环境相关信息：
操作系统：{self.os_env}
所在目录：'/home/liborui/Documents/workspace/'
            """
        return sys + soul
