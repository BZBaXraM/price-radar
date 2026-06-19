"""Baku Electronics scraper — Next.js __NEXT_DATA__ JSON in category pages."""
from __future__ import annotations

import json
import re

from app.config import settings
from app.scrapers.base import BaseScraper, ScrapedItem
from app.scrapers.http_client import fetch_text, make_client
from app.scrapers.registry import CATEGORIES, STORE_DEFS

_NEXT_DATA_RE = re.compile(
    r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', re.S
)


class BakuElectronicsScraper(BaseScraper):
    slug = "bakuelectronics"
    name = STORE_DEFS["bakuelectronics"]["name"]
    base_url = STORE_DEFS["bakuelectronics"]["base_url"]
    requires_browser = False

    @staticmethod
    def parse(html: str, category: str | None = None) -> list[ScrapedItem]:
        m = _NEXT_DATA_RE.search(html)
        if not m:
            return []
        data = json.loads(m.group(1))
        try:
            block = data["props"]["pageProps"]["products"]["products"]
        except (KeyError, TypeError):
            return []
        items = block.get("items") if isinstance(block, dict) else block
        if not items:
            return []

        out: list[ScrapedItem] = []
        for it in items:
            name = (it.get("name") or "").strip()
            slug = it.get("slug")
            if not name or not slug:
                continue
            price = it.get("discounted_price") or it.get("price")
            if not price:
                continue
            out.append(
                ScrapedItem(
                    store_slug="bakuelectronics",
                    source_url=f"https://bakuelectronics.az/mehsul/{slug}",
                    raw_title=name,
                    price=float(price),
                    image_url=it.get("image"),
                    in_stock=bool(it.get("quantity", 0)) or bool(it.get("is_online")),
                    category=category,
                )
            )
        return out

    async def run(self, limit: int = 60) -> list[ScrapedItem]:
        results: list[ScrapedItem] = []
        async with make_client() as client:
            for path in CATEGORIES["bakuelectronics"]:
                category = path.strip("/").split("/")[-1]
                for page in range(1, settings.scrape_max_pages + 1):
                    if len(results) >= limit:
                        break
                    sep = "&" if "?" in path else "?"
                    try:
                        html = await fetch_text(client, f"{self.base_url}{path}{sep}page={page}")
                    except Exception:
                        break
                    items = self.parse(html, category=category)
                    if not items:  # past the last page
                        break
                    results.extend(items)
                if len(results) >= limit:
                    break
        return results[:limit]
