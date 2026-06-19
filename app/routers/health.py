"""Health and meta endpoints."""
from __future__ import annotations

from fastapi import APIRouter

from app.config import settings

router = APIRouter(tags=["meta"])


@router.get("/health")
async def health():
    return {"status": "ok", "service": "price-radar", "langs": list(settings.supported_langs)}
