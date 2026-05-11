from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
from core.database import get_db
from core.security import get_current_user
from models.user import User
from models.other import ChatSession, ChatMessage
from schemas.main import ChatRequest, ChatResponse, ChatSessionOut
from services.chatbot import get_nour_response
import uuid

router = APIRouter(prefix="/chat", tags=["AI Chatbot"])


@router.post("/", response_model=ChatResponse)
async def chat(
    data: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Get or create session
    session = None
    if data.session_id:
        result = await db.execute(
            select(ChatSession).where(
                ChatSession.id == data.session_id,
                ChatSession.user_id == current_user.id,
            )
        )
        session = result.scalar_one_or_none()

    if not session:
        session = ChatSession(
            id=uuid.uuid4(),
            user_id=current_user.id,
            title=data.message[:60] + ("..." if len(data.message) > 60 else ""),
        )
        db.add(session)
        await db.flush()

    # Load conversation history (last 20 messages for context)
    history_result = await db.execute(
        select(ChatMessage)
        .where(ChatMessage.session_id == session.id)
        .order_by(ChatMessage.sent_at.asc())
        .limit(20)
    )
    history = history_result.scalars().all()

    messages = [{"role": m.role, "content": m.content} for m in history]
    messages.append({"role": "user", "content": data.message})

    # Call AI
    reply, tokens_used = await get_nour_response(messages)

    # Save user message
    user_msg = ChatMessage(
        session_id=session.id,
        role="user",
        content=data.message,
    )
    db.add(user_msg)

    # Save assistant reply
    now = datetime.utcnow()
    bot_msg = ChatMessage(
        session_id=session.id,
        role="assistant",
        content=reply,
        tokens_used=tokens_used,
        sent_at=now,
    )
    db.add(bot_msg)
    session.message_count = (session.message_count or 0) + 2

    await db.commit()

    return ChatResponse(session_id=session.id, reply=reply, sent_at=now)


@router.get("/sessions", response_model=list[ChatSessionOut])
async def list_sessions(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(ChatSession)
        .where(ChatSession.user_id == current_user.id)
        .order_by(ChatSession.started_at.desc())
        .limit(30)
    )
    return [ChatSessionOut.model_validate(s) for s in result.scalars().all()]


@router.get("/sessions/{session_id}", response_model=ChatSessionOut)
async def get_session(
    session_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(ChatSession).where(
            ChatSession.id == session_id,
            ChatSession.user_id == current_user.id,
        )
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    msg_result = await db.execute(
        select(ChatMessage)
        .where(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.sent_at.asc())
    )
    session.messages = msg_result.scalars().all()
    return ChatSessionOut.model_validate(session)


@router.delete("/sessions/{session_id}", status_code=204)
async def delete_session(
    session_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(ChatSession).where(
            ChatSession.id == session_id,
            ChatSession.user_id == current_user.id,
        )
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    await db.delete(session)
    await db.commit()
