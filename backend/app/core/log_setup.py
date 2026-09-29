import sys
from loguru import logger
import logging

logger.remove()


class InterceptHandler(logging.Handler):
    """把标准库日志转到 loguru"""

    def emit(self, record: logging.LogRecord):
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno
        frame, depth = logging.currentframe(), 2
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1
        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


def setup_log():
    logging.basicConfig(handlers=[InterceptHandler()], level=logging.INFO)
    _format = "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <lvl>{level: <8}</lvl> | <cyan>{name}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
    logger.add(
        sys.stdout,
        colorize=True,
        format=_format,
    )

    logger.add(
        "app.log",
        colorize=True,
        format=_format,
        rotation="10 MB",  # 按文件大小轮转
        retention="7 days",  # 按时间自动清理老日志
        level="INFO",
        enqueue=True,
    )
    logging.basicConfig(handlers=[InterceptHandler()], level=logging.INFO)
    for name in ["uvicorn", "uvicorn.access", "uvicorn.error", "fastapi"]:
        _log = logging.getLogger(name)
        _log.handlers = [InterceptHandler()]
        _log.propagate = False
