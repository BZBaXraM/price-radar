"""KontaktHome (kontakt.az) scraper.

The site is behind Cloudflare, so pages are loaded with a headless browser.
Each product tile carries a ``data-gtm`` JSON blob with name/brand/price/category,
which we parse directly. Degrades gracefully (returns []) if the browser or
Cloudflare challenge fails — other stores keep working.
"""
from __future__ import annotations

import json
import re

from selectolax.parser import HTMLParser

from app.scrapers.base import BaseScraper, OfferSnapshot, ScrapedItem
from app.scrapers.base import parse_price
from app.scrapers.registry import CATEGORIES, STORE_DEFS

_JSONLD_PRICE_RE = re.compile(r'"price"\s*:\s*"?([\d.,]+)"?')


class KontaktScraper(BaseScraper):
    slug = "kontakt"
    name = STORE_DEFS["kontakt"]["name"]
    base_url = STORE_DEFS["kontakt"]["base_url"]
    requires_browser = True

    @staticmethod
    def parse_cards(html: str, category: str | None = None) -> list[ScrapedItem]:
        tree = HTMLParser(html)
        out: list[ScrapedItem] = []
        seen: set[str] = set()
        for card in tree.css(".product-item"):
            gtm = card.attributes.get("data-gtm")
            if not gtm:
                continue
            try:
                info = json.loads(gtm)
            except (json.JSONDecodeError, TypeError):
                continue
            name = (info.get("item_name") or "").strip()
            price = info.get("price")
            if not name or not price:
                continue

            # product link: first anchor whose href is a product slug
            href = None
            for a in card.css("a"):
                h = a.attributes.get("href") or ""
                if h.startswith("https://kontakt.az/") and h.count("/") == 3 and "#" not in h:
                    href = h
                    break
            if not href:
                href = f"https://kontakt.az/catalog/product/view/id/{card.attributes.get('id', '')}"
            if href in seen:
                continue
            seen.add(href)

            img_el = card.css_first(".product-image img") or card.css_first("img")
            image_url = None
            if img_el:
                image_url = img_el.attributes.get("src") or img_el.attributes.get("data-src")

            out.append(
                ScrapedItem(
                    store_slug="kontakt",
                    source_url=href,
                    raw_title=name,
                    price=float(price),
                    image_url=image_url,
                    in_stock=True,
                    brand=info.get("item_brand") or None,
                    category=info.get("item_category") or category,
                )
            )
        return out

    @staticmethod
    def parse_detail(html: str) -> OfferSnapshot | None:
        tree = HTMLParser(html)
        # Prefer Open Graph / JSON-LD price exposed on the product page.
        meta = tree.css_first('meta[property="product:price:amount"]') or tree.css_first(
            'meta[property="og:price:amount"]'
        )
        price = parse_price(meta.attributes.get("content")) if meta else None
        if not price:
            m = _JSONLD_PRICE_RE.search(html)
            price = parse_price(m.group(1)) if m else None
        if not price:
            return None
        avail = tree.css_first('meta[property="product:availability"]')
        in_stock = True
        if avail:
            in_stock = "out" not in (avail.attributes.get("content") or "").lower()
        return OfferSnapshot(price=price, in_stock=in_stock)

    async def fetch_offer(self, url: str) -> OfferSnapshot | None:
        # Best-effort: kontakt is behind Cloudflare and needs a browser render,
        # so this is slow; the refresh service skips it unless explicitly asked.
        from app.scrapers.browser import get_rendered_html

        try:
            html = await get_rendered_html(url, timeout_ms=40000)
        except Exception:
            return None
        return self.parse_detail(html)

    async def run(self, limit: int = 60) -> list[ScrapedItem]:
        from app.scrapers.browser import get_rendered_html

        results: list[ScrapedItem] = []
        for path in CATEGORIES["kontakt"]:
            if len(results) >= limit:
                break
            try:
                html = await get_rendered_html(
                    self.base_url + path, wait_selector=".product-item", timeout_ms=40000
                )
            except Exception:
                # Cloudflare/browser failure → skip; store marked unavailable upstream.
                continue
            results.extend(self.parse_cards(html))
        return results[:limit]
