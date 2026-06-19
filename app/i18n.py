"""Lightweight i18n for API labels, statuses and AI system messages."""
from __future__ import annotations

from app.config import settings

# key -> {lang: text}
CATALOG: dict[str, dict[str, str]] = {
    "in_stock": {"az": "Mövcuddur", "ru": "В наличии", "en": "In stock"},
    "out_of_stock": {"az": "Mövcud deyil", "ru": "Нет в наличии", "en": "Out of stock"},
    "best_price": {"az": "Ən sərfəli qiymət", "ru": "Лучшая цена", "en": "Best price"},
    "offers": {"az": "Təkliflər", "ru": "Предложения", "en": "Offers"},
    "store_unavailable": {
        "az": "Mağaza müvəqqəti əlçatan deyil",
        "ru": "Магазин временно недоступен",
        "en": "Store temporarily unavailable",
    },
    "ai_offtopic": {
        "az": "Mən yalnız məhsullar, qiymətlər və mövcudluq haqqında suallara cavab verə bilərəm.",
        "ru": "Я могу отвечать только на вопросы о товарах, ценах и наличии.",
        "en": "I can only answer questions about products, prices and availability.",
    },
    "ai_no_data": {
        "az": "Bu sorğu üzrə məhsul tapılmadı.",
        "ru": "По этому запросу товары не найдены.",
        "en": "No products found for this query.",
    },
}

LANG_NAMES = {"az": "Azərbaycan dili", "ru": "Русский", "en": "English"}


def normalize_lang(lang: str | None) -> str:
    if not lang:
        return settings.default_lang
    code = lang.strip().lower().split("-")[0].split(",")[0]
    return code if code in settings.supported_langs else settings.default_lang


def t(key: str, lang: str) -> str:
    lang = normalize_lang(lang)
    entry = CATALOG.get(key, {})
    return entry.get(lang) or entry.get(settings.default_lang) or key
