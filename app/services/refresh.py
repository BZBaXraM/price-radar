"""On-demand refresh of a single product's offers.

Re-fetches each of a product's offer pages directly (a point lookup, not a
category crawl), updates any changed price/stock, writes ``PriceHistory``, and
broadcasts the changes over the same WebSocket channel the scheduler uses.
Browser-backed stores (kontakt) are skipped by default to keep the request fast.
"""
from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Offer, PriceHistory, Product
from app.scrapers.base import OfferSnapshot
from app.scrapers.registry import get_scraper
from app.services.ws_manager import price_manager

log = logging.getLogger("price_radar.refresh")

# Per-product locks so concurrent requests for the same product don't stampede
# the stores (and don't double-write history).
_locks: dict[int, asyncio.Lock] = {}


async def _snapshot(offer: Offer) -> tuple[Offer, OfferSnapshot | None]:
    """Fetch a fresh snapshot for one offer (network only — no DB access)."""
    scraper = get_scraper(offer.store.slug)
    if scraper is None:
        return offer, None
    try:
        snap = await scraper.fetch_offer(offer.source_url)
    except Exception as exc:  # graceful: keep last known values for this offer
        log.warning("refresh fetch failed for %s: %s", offer.source_url, exc)
        snap = None
    return offer, snap


async def refresh_product(
    session: AsyncSession, product_id: int, include_slow: bool = False
) -> dict | None:
    """Re-scrape a single product's offers. Returns a summary, or ``None`` if the
    product doesn't exist. ``include_slow`` also refreshes browser-backed stores.
    """
    product = await session.scalar(
        select(Product)
        .where(Product.id == product_id)
        .options(selectinload(Product.offers).selectinload(Offer.store))
    )
    if product is None:
        return None

    lock = _locks.setdefault(product_id, asyncio.Lock())
    if lock.locked():
        return {"product_id": product_id, "status": "in_progress", "checked": 0,
                "refreshed": 0, "changes": []}

    async with lock:
        targets = [
            o for o in product.offers
            if o.store and (include_slow or not o.store.requires_browser)
        ]
        results = await asyncio.gather(*(_snapshot(o) for o in targets))

        now = datetime.now(timezone.utc)
        changes: list[dict] = []
        refreshed = 0
        for offer, snap in results:
            if snap is None:
                continue
            refreshed += 1
            price_changed = abs(offer.price - snap.price) > 0.001
            stock_changed = offer.in_stock != snap.in_stock
            if price_changed or stock_changed:
                old_price = offer.price
                offer.price = snap.price
                offer.in_stock = snap.in_stock
                if snap.image_url and not offer.image_url:
                    offer.image_url = snap.image_url
                offer.scraped_at = now
                session.add(
                    PriceHistory(offer_id=offer.id, price=snap.price, in_stock=snap.in_stock)
                )
                changes.append(
                    {
                        "product_id": product.id,
                        "product_title": product.title,
                        "store_slug": offer.store.slug,
                        "old_price": old_price,
                        "new_price": snap.price,
                        "in_stock": snap.in_stock,
                        "currency": offer.currency,
                        "observed_at": now,
                    }
                )
            else:
                offer.scraped_at = now
        await session.commit()

    await price_manager.broadcast_changes(changes)
    return {
        "product_id": product_id,
        "status": "ok",
        "checked": len(targets),
        "refreshed": refreshed,
        "changes": changes,
    }
