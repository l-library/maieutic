from fastapi import APIRouter
from openai import BaseModel
import asyncio
from app.agent.llm import generate
from app.agent.agent import agent

router = APIRouter()


_agent = agent()


class Message(BaseModel):
    message: str


class ModelResponse(BaseModel):
    type: str
    content: str


@router.get("/")
def llm_alive():
    return {"llm test": generate("hello")[0]}


@router.post("/chat/", response_model=list[ModelResponse])
def llm_chat(message: Message):
    res = asyncio.run(_agent.core_loop((message.message)))
    return res
