"""
对话api
"""

from fastapi import APIRouter
from fastapi.sse import EventSourceResponse
from openai import BaseModel
from app.agent.llm import generate
from app.agent.agent import agent

router = APIRouter()


_conversations: dict[str, agent] = {}


class Message(BaseModel):
    message: str


class ModelResponse(BaseModel):
    type: str
    content: str


@router.get("/")
def llm_alive():
    return {"llm test": generate("hello")[0]}


@router.post(
    "/chat/{conversation_id}",
    response_model=ModelResponse,
    response_class=EventSourceResponse,
)
async def llm_chat(conversation_id: str, message: Message):
    try:
        _agent = _conversations[conversation_id]
    except KeyError:
        _agent = agent()
        _conversations[conversation_id] = _agent
    async for piece in _agent.core_loop(message.message):
        yield piece
