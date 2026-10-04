"""
对话api
"""

from fastapi import APIRouter
from fastapi.sse import EventSourceResponse
from openai import BaseModel
from app.agent.llm import LLM
from app.agent.agent import agent

router = APIRouter()


_conversations: dict[str, agent] = {}


_llm_client = None


def _get_llm_client():
    global _llm_client
    if _llm_client is None:
        _llm_client = LLM()
    return _llm_client


class Message(BaseModel):
    message: str


class ModelResponse(BaseModel):
    type: str
    content: str


@router.get("/")
def llm_alive():
    return {"llm test": _get_llm_client().generate("hello")[0]}


@router.post(
    "/chat/{conversation_id}",
    response_model=ModelResponse,
    response_class=EventSourceResponse,
)
async def llm_chat(conversation_id: str, message: Message):
    try:
        _agent = _conversations[conversation_id]
    except KeyError:
        _agent = agent(_get_llm_client())
        _conversations[conversation_id] = _agent
    async for piece in _agent.core_loop(message.message):
        yield piece
