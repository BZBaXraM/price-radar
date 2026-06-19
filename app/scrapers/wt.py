"""World Telecom (w-t.az) scraper — server-rendered .productCard grid."""
from __future__ import annotations

import re

from selectolax.parser import HTMLParser

from app.config import settings
from app.scrapers.base import BaseScraper, ScrapedItem, parse_price
from app.scrapers.http_client import fetch_text, make_client
from app.scrapers.registry import CATEGORIES, STORE_DEFS


class WorldTelecomScraper(BaseScraper):
    slug = "wt"
    name = STORE_DEFS["wt"]["name"]
    base_url = STORE_DEFS["wt"]["base_url"]
    requires_browser = False

    @staticmethod
    def parse_cards(html: str, category: str | None = None) -> list[ScrapedItem]:
        tree = HTMLParser(html)
        out: list[ScrapedItem] = []
        for card in tree.css(".productCard"):
            name_el = card.css_first(".productName")
            link_el = card.css_first(".productNameUrl a") or card.css_first("a.productUrl") or card.css_first("a")
            if not name_el or not link_el:
                continue
            title = re.sub(r"\s+", " ", name_el.text()).strip()
            href = link_el.attributes.get("href") or ""
            if not title or not href:
                continue

            price_el = card.css_first(".productPrice .realPrice") or card.css_first(".productPrice")
            price = parse_price(price_el.text()) if price_el else None
            if not price:
                continue

            img = card.css_first(".productImage-img") or card.css_first("img")
            image_url = None
            if img:
                image_url = img.attributes.get("src") or img.attributes.get("data-src")

            out.append(
                ScrapedItem(
                    store_slug="wt",
                    source_url=href if href.startswith("http") else "https://w-t.az" + href,
                    raw_title=title,
                    price=price,
                    image_url=image_url,
                    in_stock="out-of-stock" not in (card.attributes.get("class") or ""),
                    category=category,
                )
            )
        return out

    async def run(self, limit: int = 60) -> list[ScrapedItem]:
        results: list[ScrapedItem] = []
        seen: set[str] = set()
        async with make_client() as client:
            for path in CATEGORIES["wt"]:
                category = path.split("+")[-1]
                for page in range(1, settings.scrape_max_pages + 1):
                    if len(results) >= limit:
                        break
                    try:
                        html = await fetch_text(
                            client, f"{self.base_url}{path}?locale=az&page={page}"
                        )
                    except Exception:
                        break
                    items = self.parse_cards(html, category=category)
                    # Stop when a page yields no new products (end / repeated page).
                    new = [it for it in items if it.source_url not in seen]
                    if not new:
                        break
                    seen.update(it.source_url for it in new)
                    results.extend(new)
                if len(results) >= limit:
                    break
        return results[:limit]
