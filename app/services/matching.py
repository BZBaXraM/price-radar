"""Cross-store product matching.

Builds a normalized ``group_key`` (brand|model|storage) so the same product from
different stores collapses into one canonical Product. ``token_set_ratio`` is used
as a fuzzy fallback when keys don't match exactly.
"""
from __future__ import annotations

import re
import unicodedata

from rapidfuzz import fuzz

# Known brands across these electronics stores (extend as needed).
BRANDS = [
    "apple", "iphone", "ipad", "macbook", "samsung", "xiaomi", "redmi", "poco",
    "huawei", "honor", "lenovo", "asus", "acer", "hp", "dell", "msi", "lg",
    "sony", "bosch", "beko", "indesit", "hoffmann", "philips", "panasonic",
    "canon", "nikon", "fujifilm", "gopro", "dyson", "tefal", "delonghi",
    "electrolux", "aeg", "braun", "realme", "oppo", "vivo", "google", "nokia",
    "tcl", "hisense", "haier", "whirlpool", "siemens", "jbl", "marshall",
]

# Apple sub-brands map to "apple".
_APPLE_ALIASES = {"iphone", "ipad", "macbook"}

_STORAGE_RE = re.compile(r"(\d+)\s?(tb|gb)\b", re.I)
_SCREEN_RE = re.compile(r"(\d{2}(?:[.,]\d)?)\s?(?:\"|inch|''|″)", re.I)
_NOISE = re.compile(
    r"\b(smartfon|telefon|planşet|planshet|notbuk|notebook|noutbuk|tv|televizor|"
    r"soyuducu|paltaryuyan|wi-fi|wifi|with|chip|ssd|ram|ddr\d?x?|fhd|qhd|oled|ips|gb|tb)\b",
    re.I,
)

# Colour words across az/ru/en — colour variants share the same model for pricing.
_COLORS = re.compile(
    r"\b(black|white|silver|gold|blue|red|green|gray|grey|pink|purple|orange|"
    r"yellow|titanium|graphite|midnight|starlight|qara|ag|gümüşü|mavi|qirmizi|"
    r"yasil|boz|чёрный|черный|белый|серебристый|золотой|синий|красный|зелёный|"
    r"серый|розовый|cosmic|natural|desert|teal|lilac|blossom|coral|cyan|beige)\b",
    re.I,
)


def _strip_accents(text: str) -> str:
    nfkd = unicodedata.normalize("NFKD", text)
    return "".join(c for c in nfkd if not unicodedata.combining(c))


def normalize_title(title: str) -> str:
    t = _strip_accents(title.lower())
    t = re.sub(r"[\(\)\[\]/,;:+]", " ", t)
    t = _COLORS.sub(" ", t)
    t = _NOISE.sub(" ", t)
    t = re.sub(r"[^a-z0-9\.\" ]", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def extract_brand(title: str, hint: str | None = None) -> str | None:
    if hint:
        h = hint.strip().lower()
        if h in _APPLE_ALIASES:
            return "apple"
        if h:
            return h
    norm = normalize_title(title)
    for b in BRANDS:
        if re.search(rf"\b{re.escape(b)}\b", norm):
            return "apple" if b in _APPLE_ALIASES else b
    return None


def extract_storage(title: str) -> str | None:
    m = _STORAGE_RE.search(title)
    if not m:
        return None
    return f"{m.group(1)}{m.group(2).lower()}"


def extract_screen(title: str) -> str | None:
    m = _SCREEN_RE.search(title)
    return m.group(1).replace(",", ".") if m else None


def model_core(title: str, brand: str | None) -> str:
    # Drop storage/screen tokens up front so "256gb" and "256 gb" don't diverge.
    title = _STORAGE_RE.sub(" ", title)
    title = _SCREEN_RE.sub(" ", title)
    norm = normalize_title(title)
    if brand:
        norm = re.sub(rf"\b{re.escape(brand)}\b", "", norm)
        for alias in _APPLE_ALIASES:
            if brand == "apple":
                norm = re.sub(rf"\b{alias}\b", alias, norm)  # keep iphone/ipad token
    # keep alphanumeric model tokens, drop pure colour words is hard; keep first 6 tokens
    tokens = [tok for tok in norm.split() if tok]
    return " ".join(tokens[:8]).strip()


def group_key(title: str, brand_hint: str | None = None) -> str:
    brand = extract_brand(title, brand_hint) or "unknown"
    storage = extract_storage(title) or ""
    screen = extract_screen(title) or ""
    core = model_core(title, brand if brand != "unknown" else None)
    return f"{brand}|{core}|{storage}|{screen}".strip("|")


def similarity(a: str, b: str) -> float:
    return fuzz.token_set_ratio(normalize_title(a), normalize_title(b))


# Two titles are considered the same product above this fuzzy threshold.
MATCH_THRESHOLD = 88.0
