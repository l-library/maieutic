from fastapi import APIRouter
from openai import BaseModel
import asyncio
from app.agent.llm import generate
from app.agent.agent import agent

router = APIRouter()


_conversations: dict[int, agent] = {}


class Message(BaseModel):
    message: str


class ModelResponse(BaseModel):
    type: str
    content: str


@router.get("/")
def llm_alive():
    return {"llm test": generate("hello")[0]}


@router.post("/chat/{conversation_id}", response_model=list[ModelResponse])
def llm_chat(conversation_id: int, message: Message):
    try:
        _agent = _conversations[conversation_id]
    except KeyError:
        _agent = agent()
        _conversations[conversation_id] = _agent
    res = asyncio.run(_agent.core_loop(message.message))
    return res
