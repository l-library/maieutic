"""
处理对话相关业务
"""

import asyncio
import time

from loguru import logger
from openai.types.chat import ChatCompletionMessageParam
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agent.llm import LLM
from app.agent.prompt import Prompt
from app.models.conversation import Conversation


async def get_conversation(
    session: AsyncSession, _id: int
) -> list[ChatCompletionMessageParam]:
    """
    查：对话历史
    """
    conv = await session.get(Conversation, _id)
    if conv is None:
        raise ValueError(f"Conversation {_id} is not exists")
    return conv.messages


async def get_list(session: AsyncSession) -> list[dict]:
    """查：查询 conversation list"""
    stmt = select(
        Conversation.id,
        Conversation.title,
        Conversation.create_time,
        Conversation.change_time,
    )
    result = await session.execute(stmt)
    res: list[dict] = []
    for conv in result:
        res.append(
            {
                "id": conv.id,
                "title": conv.title,
                "create_time": conv.create_time,
                "change_time": conv.change_time,
            }
        )
    return res


async def create_conversation(title: str, session: AsyncSession) -> int:
    """
    增：创建对话，返回对话 id
    创建时自动插入创建&修改时间
    """
    # 如果最近一次更新的对话为空对话，则不创建新对话
    statement = (
        select(Conversation.id, Conversation.messages)
        .order_by(Conversation.create_time.desc(), Conversation.id.desc())
        .limit(1)
    )
    latest = (await session.execute(statement)).first()
    if latest is not None and not latest.messages:
        logger.info("最新对话为空，复用……")
        return latest.id

    now = int(time.time())
    conv = Conversation(title=title, create_time=now, change_time=now)
    session.add(conv)
    await session.commit()
    return conv.id


async def append_new_messages(
    session: AsyncSession, _id: int, new_messages: list[ChatCompletionMessageParam]
) -> bool:
    """增：向指定对话插入新消息"""
    conv = await session.get(Conversation, _id)
    if conv is None:
        raise ValueError(f"Conversation {_id} is not exists")
    conv.messages += new_messages
    await session.commit()
    return True


async def auto_name_conversation(session: AsyncSession, _id: int, _llm: LLM):
    """改：为给定 id 的对话，调用 llm 重命名，llm 不可用时自动降级"""
    history = await get_conversation(session, _id)
    conv = await session.get(Conversation, _id)

    if history is None or conv is None:
        raise ValueError(f"Conversation {_id} is not exists")
    if conv.title != "新对话":
        return ""

    try:
        title = await asyncio.to_thread(
            _llm.generate, Prompt().get_title_generate_prompt() + str(history)
        )
    except Exception as e:  # noqa: BLE001
        logger.warning(f"对话自动命名失败，保持“新对话”：{e!s}")
        return ""

    # 入库
    conv.title = title
    await session.commit()

    logger.info(f"对话自动命名：[{title}]")

    return title
