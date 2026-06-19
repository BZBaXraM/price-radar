"""Tests for the AI assistant tool layer and guardrail fallbacks (no network)."""
import json

import pytest

from app.scrapers.base import ScrapedItem
from app.services import ai_assistant
from app.services.ingest import ingest_items
from app.i18n import t


@pytest.mark.asyncio
async def test_search_tool_returns_db_grounded_data(session):
    await ingest_items(
        session,
        [ScrapedItem("kontakt", "https://kontakt.az/iphone-15", "iPhone 15 256 GB Black", 1969.99, brand="Apple")],
    )
    result, rows = await ai_assistant._run_tool(session, "search_products", {"q": "iphone"})
    payload = json.loads(result)
    assert payload["total"] == 1
    assert rows and rows[0]["best_price"] == 1969.99


@pytest.mark.asyncio
async def test_no_api_key_degrades_gracefully(session, monkeypatch):
    monkeypatch.setattr(ai_assistant.settings, "zai_api_key", "")
    out = await ai_assistant.answer(session, "hello", lang="en")
    assert out["lang"] == "en"
    assert out["reply"] == t("ai_offtopic", "en")
    assert out["used_products"] == []


@pytest.mark.asyncio
async def test_unknown_tool_is_safe(session):
    result, rows = await ai_assistant._run_tool(session, "delete_everything", {})
    assert "error" in result
    assert rows == []
