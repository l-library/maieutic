"""
conversation 表映射
"""

from openai.types.chat import ChatCompletionMessageParam
from sqlalchemy import JSON, String, Integer
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy.orm import Mapped, mapped_column
import time

from app.models.base import Base


class Conversation(Base):
    __doc__ = "存储用户与agent的对话历史"
    __tablename__ = "conversation"

    id: Mapped[int] = mapped_column(primary_key=True, doc="主键，自增")

    title: Mapped[str] = mapped_column(String(50), doc="对话标题")
    messages: Mapped[list[ChatCompletionMessageParam]] = mapped_column(
        MutableList.as_mutable(JSON),
        default=list,
        doc="每轮消息，type表示类型，content为消息内容",
    )
    create_time: Mapped[int] = mapped_column(Integer, doc="创建时间")
    change_time: Mapped[int] = mapped_column(Integer, doc="修改时间")


# TODO: 创建时间 & 修改时间
