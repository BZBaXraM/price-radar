"""Base scraper contract shared by all stores."""
from __future__ import annotations

import re
from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass(slots=True)
class ScrapedItem:
    """A normalized product listing produced by any scraper."""

    store_slug: str
    source_url: str
    raw_title: str
    price: float
    currency: str = "AZN"
    in_stock: bool = True
    image_url: str | None = None
    brand: str | None = None
    category: str | None = None
    extra: dict = field(default_factory=dict)


@dataclass(slots=True)
class OfferSnapshot:
    """Fresh price/stock for a single known offer page (on-demand refresh)."""

    price: float
    in_stock: bool = True
    image_url: str | None = None


_PRICE_RE = re.compile(r"[\d][\d\s.,]*")


def parse_price(text: str | None) -> float | None:
    """Extract a numeric price from messy strings like '1 299,00 ₼' or '2.499 AZN'."""
    if not text:
        return None
    m = _PRICE_RE.search(text.replace("\xa0", " "))
    if not m:
        return None
    raw = m.group(0).strip().replace(" ", "")
    # Handle thousands/decimal separators: keep the last separator as decimal.
    if "," in raw and "." in raw:
        raw = raw.replace(".", "").replace(",", ".") if raw.rfind(",") > raw.rfind(".") else raw.replace(",", "")
    elif "," in raw:
        # comma is decimal if it precedes exactly 2 digits, else thousands sep
        raw = raw.replace(",", ".") if re.search(r",\d{2}$", raw) else raw.replace(",", "")
    elif raw.count(".") > 1:
        raw = raw.replace(".", "")
    try:
        val = float(raw)
    except ValueError:
        return None
    return val if val > 0 else None


class BaseScraper(ABC):
    slug: str
    name: str
    base_url: str
    requires_browser: bool = False

    @abstractmethod
    async def run(self, limit: int = 60) -> list[ScrapedItem]:
        """Scrape up to ``limit`` products and return normalized items."""
        raise NotImplementedError

    async def fetch_offer(self, url: str) -> "OfferSnapshot | None":
        """Re-fetch a single known product page for an on-demand refresh.

        Returns fresh price/stock, or ``None`` when the page can't be read
        (so the caller keeps the last known values). Opt-in per store.
        """
        return None
