"""WebSocket connection manager for broadcasting real-time price updates."""
from __future__ import annotations

import asyncio
from datetime import datetime

from fastapi import WebSocket


def _json_default(o):
    if isinstance(o, datetime):
        return o.isoformat()
    return str(o)


class ConnectionManager:
    def __init__(self) -> None:
        self._connections: set[WebSocket] = set()
        self._lock = asyncio.Lock()

    async def connect(self, ws: WebSocket) -> None:
        await ws.accept()
        async with self._lock:
            self._connections.add(ws)

    async def disconnect(self, ws: WebSocket) -> None:
        async with self._lock:
            self._connections.discard(ws)

    async def broadcast(self, message: dict) -> None:
        async with self._lock:
            targets = list(self._connections)
        dead: list[WebSocket] = []
        for ws in targets:
            try:
                await ws.send_json(message)
            except Exception:
                dead.append(ws)
        if dead:
            async with self._lock:
                for ws in dead:
                    self._connections.discard(ws)

    async def broadcast_changes(self, changes: list[dict]) -> None:
        if not changes:
            return
        # Serialize datetimes for transport.
        payload = {
            "type": "price_updates",
            "count": len(changes),
            "changes": [
                {**c, "observed_at": _json_default(c.get("observed_at"))} for c in changes
            ],
        }
        await self.broadcast(payload)


# Single app-wide manager instance.
price_manager = ConnectionManager()
