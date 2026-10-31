"""
对话api
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.sse import EventSourceResponse
from openai import BaseModel
from openai.types.chat import ChatCompletionMessageParam
from sqlalchemy.ext.asyncio import AsyncSession

from app.agent.agent import core_loop
from app.agent.llm import LLM
from app.db.engine import get_db
from app.services import conversation as conversation_service

router = APIRouter()

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


class ConversationElement(BaseModel):
    id: int
    title: str
    create_time: int
    change_time: int


@router.get("/")
def llm_alive():
    return {"llm test": _get_llm_client().generate("hello")[0]}


@router.get(
    "/conversation/get/{conversation_id}",
    response_model=list[ChatCompletionMessageParam],
)
async def get_conversation(
    conversation_id: int, session: Annotated[AsyncSession, Depends(get_db)]
):
    """
    利用 conversation id 获取对话
    """
    try:
        conv = await conversation_service.get_conversation(session, conversation_id)
    except ValueError:
        raise HTTPException(404, detail="对话不存在")
    return conv


@router.post(
    "/conversation/chat/{conversation_id}",
    response_model=ModelResponse,
    response_class=EventSourceResponse,
)
async def llm_chat(
    conversation_id: int,
    message: Message,
    session: Annotated[AsyncSession, Depends(get_db)],
):
    """
    传入对话id，使用那个id的对话历史
    """
    conv = await conversation_service.get_conversation(session, conversation_id)
    async for piece in core_loop(
        history=conv,
        user_message=message.message,
        llm=_get_llm_client(),
        db_session=session,
        conversation_id=conversation_id,
    ):
        yield piece
    await conversation_service.auto_name_conversation(
        session, conversation_id, _get_llm_client()
    )


@router.get("/conversation/create")
async def create_conversation(session: Annotated[AsyncSession, Depends(get_db)]):
    """
    创建对话，返回对话id
    """
    _id = await conversation_service.create_conversation("新对话", session)
    return _id


@router.get("/conversation/list", response_model=list[ConversationElement])
async def get_conversation_list(session: Annotated[AsyncSession, Depends(get_db)]):
    """
    获取对话清单
    """
    _list = await conversation_service.get_list(session)
    return _list
