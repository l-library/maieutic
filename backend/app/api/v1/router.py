from app.api.v1.endpoints import conversations
from fastapi import APIRouter

api_router = APIRouter()

api_router.include_router(conversations.router, tags=["普通对话"])
