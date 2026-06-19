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
    # Category labels — keys match URL slugs stored in Product.category
    "telefonlar-plansetler": {"az": "Telefon və Planşetlər", "ru": "Телефоны и Планшеты", "en": "Phones & Tablets"},
    "noutbuklar-komputerler-planshetler": {"az": "Noutbuk və Kompüterlər", "ru": "Ноутбуки и Компьютеры", "en": "Laptops & Computers"},
    "noutbuklar": {"az": "Noutbuklar", "ru": "Ноутбуки", "en": "Laptops"},
    "soyuducular": {"az": "Soyuducular", "ru": "Холодильники", "en": "Refrigerators"},
    "paltaryuyan-masinlar": {"az": "Paltaryuyan Maşınlar", "ru": "Стиральные машины", "en": "Washing Machines"},
    "telefon-ve-aksesuarlar": {"az": "Telefon və Aksesuarlar", "ru": "Телефоны и аксессуары", "en": "Phones & Accessories"},
    "notbuk-planset-ve-komputer-texnikasi": {"az": "Noutbuk, Planşet və Kompüter", "ru": "Ноутбуки, Планшеты и ПК", "en": "Laptops, Tablets & PCs"},
    "foto-texnika": {"az": "Foto Texnika", "ru": "Фототехника", "en": "Photo Equipment"},
    "fotoaparatlar": {"az": "Fotoaparatlar", "ru": "Фотоаппараты", "en": "Cameras"},
    "boyuk-meiset-texnikasi": {"az": "Böyük Məişət Texnikası", "ru": "Крупная бытовая техника", "en": "Large Home Appliances"},
    "k1+telefon-plansetler-saat": {"az": "Telefon, Planşet, Saat", "ru": "Телефоны, Планшеты, Часы", "en": "Phones, Tablets & Watches"},
    "k4+noutbuk-komputer-ofis": {"az": "Noutbuk, Kompüter, Ofis", "ru": "Ноутбуки, Компьютеры, Офис", "en": "Laptops, Computers & Office"},
    "k5+tv-audio-foto": {"az": "TV, Audio, Foto", "ru": "ТВ, Аудио, Фото", "en": "TV, Audio & Photo"},
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
