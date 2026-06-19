"""Real-time price update WebSocket."""
from __future__ import annotations

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.services.ws_manager import price_manager

router = APIRouter()


@router.websocket("/ws/prices")
async def ws_prices(ws: WebSocket):
    await price_manager.connect(ws)
    try:
        await ws.send_json({"type": "connected", "message": "subscribed to price updates"})
        while True:
            # Keep the connection alive; ignore incoming payloads.
            await ws.receive_text()
    except WebSocketDisconnect:
        await price_manager.disconnect(ws)
    except Exception:
        await price_manager.disconnect(ws)
