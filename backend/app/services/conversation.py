"""
处理对话相关业务
"""

from openai.types.chat import ChatCompletionMessageParam
from sqlalchemy.ext.asyncio import AsyncSession

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


async def create_conversation(title: str, session: AsyncSession) -> int:
    """
    增：创建对话，返回对话 id
    """
    conv = Conversation(title=title)
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
