"""İrşad Electronics scraper.

Category landing pages render only a filter shell; products are served by an
AJAX endpoint referenced as ``form#categoriesFilterForm action`` (pattern
``/{lang}/list-products/{category}/{leaf}``). We resolve that endpoint and parse
the returned ``.product`` cards.
"""
from __future__ import annotations

import re

from selectolax.parser import HTMLParser

from app.scrapers.base import BaseScraper, OfferSnapshot, ScrapedItem, parse_price
from app.scrapers.http_client import fetch_text, make_client
from app.scrapers.registry import CATEGORIES, STORE_DEFS

_FORM_ACTION_RE = re.compile(
    r'<form[^>]*id="categoriesFilterForm"[^>]*action="([^"]+)"'
)


class IrshadScraper(BaseScraper):
    slug = "irshad"
    name = STORE_DEFS["irshad"]["name"]
    base_url = STORE_DEFS["irshad"]["base_url"]
    requires_browser = False

    @staticmethod
    def parse_cards(html: str, category: str | None = None) -> list[ScrapedItem]:
        tree = HTMLParser(html)
        out: list[ScrapedItem] = []
        for card in tree.css(".product"):
            name_el = card.css_first(".product__name")
            if not name_el:
                continue
            href = name_el.attributes.get("href") or ""
            title = re.sub(r"\s+", " ", name_el.text()).strip()
            if not title or not href:
                continue

            # price: prefer discounted (.new-price), fall back to current/old.
            price = None
            for sel in (".new-price", ".product__price__current", ".old-price"):
                el = card.css_first(sel)
                if el:
                    price = parse_price(el.text())
                    if price:
                        break
            if not price:
                continue

            img = card.css_first(".product__img img") or card.css_first("img")
            image_url = None
            if img:
                image_url = img.attributes.get("src") or img.attributes.get("data-src")

            out.append(
                ScrapedItem(
                    store_slug="irshad",
                    source_url=href if href.startswith("http") else "https://irshad.az" + href,
                    raw_title=title,
                    price=price,
                    image_url=image_url,
                    in_stock=True,
                    category=category,
                )
            )
        return out

    @staticmethod
    def parse_detail(html: str) -> OfferSnapshot | None:
        tree = HTMLParser(html)
        # Main product price lives in the prod-info block; scope to it so we
        # never pick up a recommended-product card's price.
        price = None
        for sel in (".prod-info__bottom__price", ".new-price", ".product-view__price"):
            el = tree.css_first(sel)
            if el:
                price = parse_price(el.text())
                if price:
                    break
        if not price:
            return None
        # No reliable in-stock marker on the detail page; mirror the listing
        # scraper, which treats İrşad products as in stock.
        return OfferSnapshot(price=price, in_stock=True)

    async def fetch_offer(self, url: str) -> OfferSnapshot | None:
        async with make_client() as client:
            try:
                html = await fetch_text(client, url)
            except Exception:
                return None
        return self.parse_detail(html)

    async def _resolve_endpoint(self, client, path: str) -> str | None:
        try:
            html = await fetch_text(client, self.base_url + path)
        except Exception:
            return None
        m = _FORM_ACTION_RE.search(html)
        if m:
            return m.group(1)
        # Fallback: derive list-products URL from the path itself.
        parts = path.strip("/").split("/")
        if len(parts) >= 2:
            lang, rest = parts[0], "/".join(parts[1:])
            return f"{self.base_url}/{lang}/list-products/{rest}"
        return None

    async def run(self, limit: int = 60) -> list[ScrapedItem]:
        results: list[ScrapedItem] = []
        async with make_client() as client:
            client.headers["X-Requested-With"] = "XMLHttpRequest"
            for path in CATEGORIES["irshad"]:
                if len(results) >= limit:
                    break
                endpoint = await self._resolve_endpoint(client, path)
                if not endpoint:
                    continue
                try:
                    html = await fetch_text(client, endpoint)
                except Exception:
                    continue
                results.extend(self.parse_cards(html, category=path.split("/")[-1]))
        return results[:limit]
