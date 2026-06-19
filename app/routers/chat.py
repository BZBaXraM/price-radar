"""AI assistant endpoints — REST and streaming-ish WebSocket."""
from __future__ import annotations

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import async_session
from app.deps import get_db
from app.i18n import normalize_lang
from app.schemas import ChatRequest, ChatResponse
from app.services import ai_assistant

router = APIRouter(prefix="/api", tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest, db: AsyncSession = Depends(get_db)):
    result = await ai_assistant.answer(db, req.message, lang=req.lang, history=req.history)
    return result


# WebSocket chat (one request/response per message over the socket).
ws_router = APIRouter()


@ws_router.websocket("/ws/chat")
async def ws_chat(ws: WebSocket):
    await ws.accept()
    try:
        while True:
            data = await ws.receive_json()
            message = data.get("message", "")
            lang = normalize_lang(data.get("lang"))
            history = data.get("history", [])
            if not message:
                await ws.send_json({"error": "empty message"})
                continue
            async with async_session() as session:
                result = await ai_assistant.answer(session, message, lang=lang, history=history)
            await ws.send_json({"type": "chat_reply", **result})
    except WebSocketDisconnect:
        return
