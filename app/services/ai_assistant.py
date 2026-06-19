"""AI assistant backed by GLM-4.7-Flash (z.ai), restricted to product/price Q&A.

Uses OpenAI-compatible tool calling so answers are grounded in the live DB
(no hallucinated prices). A strict system prompt keeps it on-topic.
"""
from __future__ import annotations

import asyncio
import json
import logging

from openai import AsyncOpenAI, APIStatusError, RateLimitError
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.i18n import LANG_NAMES, normalize_lang, t
from app.services import products as products_service

log = logging.getLogger("price_radar.ai")

SYSTEM_PROMPT = """You are PriceRadar's shopping assistant for Azerbaijani electronics stores \
(KontaktHome, İrşad, World Telecom, Baku Electronics).

STRICT SCOPE: You ONLY help with products, prices, availability, and comparing offers \
across these stores. If the user asks about anything else (general chit-chat, coding, news, \
politics, jokes, math, etc.), politely refuse with: "{refusal}" and nothing more.

Rules:
- ALWAYS use the provided tools to look up real data. Never invent products or prices.
- Prices are in AZN (₼). When comparing, state which store is cheapest and the price.
- If a search returns nothing, say so honestly: "{no_data}"
- Answer ONLY in this language: {lang_name}. Keep answers concise and helpful.
"""

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_products",
            "description": "Search products across all stores by keyword/brand/category. Returns best price per product.",
            "parameters": {
                "type": "object",
                "properties": {
                    "q": {"type": "string", "description": "Search keywords, e.g. 'iphone 15', 'soyuducu', 'laptop'"},
                    "brand": {"type": "string"},
                    "sort": {"type": "string", "enum": ["price_asc", "price_desc", "offers", "relevance"]},
                },
                "required": ["q"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_product_detail",
            "description": "Get all store offers and the best price for one product by its id.",
            "parameters": {
                "type": "object",
                "properties": {"product_id": {"type": "integer"}},
                "required": ["product_id"],
            },
        },
    },
]


def _client() -> AsyncOpenAI:
    return AsyncOpenAI(api_key=settings.zai_api_key, base_url=settings.zai_base_url)


async def _create_with_retry(client: AsyncOpenAI, **kwargs):
    """Call chat.completions with backoff on rate-limit/overload (z.ai free tier)."""
    delay = 1.0
    last_exc: Exception | None = None
    for _ in range(4):
        try:
            return await client.chat.completions.create(**kwargs)
        except (RateLimitError, APIStatusError) as exc:
            status = getattr(exc, "status_code", None)
            if status not in (429, 500, 502, 503):
                raise
            last_exc = exc
            await asyncio.sleep(delay)
            delay *= 2
    raise last_exc  # type: ignore[misc]


async def _run_tool(session: AsyncSession, name: str, args: dict) -> tuple[str, list[dict]]:
    if name == "search_products":
        rows, total = await products_service.search_products(
            session,
            q=args.get("q"),
            brand=args.get("brand"),
            sort=args.get("sort", "price_asc"),
            page_size=8,
        )
        return json.dumps({"total": total, "results": rows}, ensure_ascii=False, default=str), rows
    if name == "get_product_detail":
        detail = await products_service.get_product_detail(session, int(args.get("product_id", 0)))
        return json.dumps(detail or {}, ensure_ascii=False, default=str), ([detail] if detail else [])
    return json.dumps({"error": "unknown tool"}), []


async def answer(
    session: AsyncSession,
    message: str,
    lang: str = "az",
    history: list[dict] | None = None,
) -> dict:
    lang = normalize_lang(lang)
    system = SYSTEM_PROMPT.format(
        refusal=t("ai_offtopic", lang),
        no_data=t("ai_no_data", lang),
        lang_name=LANG_NAMES[lang],
    )
    messages = [{"role": "system", "content": system}]
    for h in (history or [])[-6:]:
        if h.get("role") in ("user", "assistant") and h.get("content"):
            messages.append({"role": h["role"], "content": h["content"]})
    messages.append({"role": "user", "content": message})

    if not settings.zai_api_key:
        return {"reply": t("ai_offtopic", lang), "lang": lang, "used_products": []}

    client = _client()
    used: list[dict] = []
    try:
        for _ in range(4):  # allow a couple of tool round-trips
            resp = await _create_with_retry(
                client,
                model=settings.zai_model,
                messages=messages,
                tools=TOOLS,
                temperature=0.2,
            )
            choice = resp.choices[0].message
            if not choice.tool_calls:
                return {"reply": choice.content or "", "lang": lang, "used_products": used}

            messages.append(
                {
                    "role": "assistant",
                    "content": choice.content or "",
                    "tool_calls": [tc.model_dump() for tc in choice.tool_calls],
                }
            )
            for tc in choice.tool_calls:
                try:
                    args = json.loads(tc.function.arguments or "{}")
                except json.JSONDecodeError:
                    args = {}
                result, rows = await _run_tool(session, tc.function.name, args)
                used.extend(r for r in rows if r)
                messages.append(
                    {"role": "tool", "tool_call_id": tc.id, "content": result}
                )
        # Fell through the loop: return last assistant content best-effort.
        return {"reply": messages[-1].get("content", "") or t("ai_no_data", lang), "lang": lang, "used_products": used}
    except Exception as exc:
        log.warning("AI request failed: %s", exc)
        return {"reply": f"{t('store_unavailable', lang)}", "lang": lang, "used_products": used}
    finally:
        await client.close()
