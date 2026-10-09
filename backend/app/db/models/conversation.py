"""
conversation 表映射
"""

from app.db.base import Base
from sqlalchemy import JSON, String
from sqlalchemy.orm import Mapped, mapped_column


class Conversation(Base):
    __doc__ = "存储用户与agent的对话历史"
    __tablename__ = "conversation"

    id: Mapped[int] = mapped_column(primary_key=True, doc="主键，自增")

    title: Mapped[str] = mapped_column(String(50), doc="对话标题")
    messages: Mapped[list[dict[str, str]]] = mapped_column(
        JSON, default=list, doc="每轮消息，type表示类型，content为消息内容"
    )
