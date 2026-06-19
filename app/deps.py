"""Shared FastAPI dependencies."""
from __future__ import annotations

from fastapi import Header, Query

from app.database import get_db  # noqa: F401  (re-exported for routers)
from app.i18n import normalize_lang


def get_lang(
    lang: str | None = Query(default=None),
    accept_language: str | None = Header(default=None),
) -> str:
    return normalize_lang(lang or accept_language)
