# app/db/models/__init__.py
from app.db.base import Base
from app.db.models.conversation import Conversation

__all__ = ["Base", "Conversation"]
