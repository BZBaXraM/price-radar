"""Ingest scraped items into the DB, grouping offers and tracking price changes."""
from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Offer, PriceHistory, Product, Store
from app.scrapers.base import ScrapedItem
from app.services import matching


async def _get_store_map(session: AsyncSession) -> dict[str, Store]:
    stores = (await session.scalars(select(Store))).all()
    return {s.slug: s for s in stores}


async def _find_or_create_product(
    session: AsyncSession,
    item: ScrapedItem,
    cache: dict[str, Product],
    brand_index: dict[str, list[Product]],
) -> Product:
    brand = matching.extract_brand(item.raw_title, item.brand)
    key = matching.group_key(item.raw_title, item.brand)

    if key in cache:
        return cache[key]

    existing = await session.scalar(select(Product).where(Product.group_key == key))
    if existing:
        cache[key] = existing
        brand_index.setdefault(brand or "unknown", []).append(existing)
        return existing

    # Fuzzy fallback: same brand AND same storage/screen, high title similarity.
    # The storage/screen guard prevents distinct SKUs (e.g. 256GB vs 512GB) from
    # collapsing into one product and corrupting the "best price".
    item_storage = matching.extract_storage(item.raw_title)
    item_screen = matching.extract_screen(item.raw_title)
    for cand in brand_index.get(brand or "unknown", []):
        if matching.extract_storage(cand.title) != item_storage:
            continue
        if matching.extract_screen(cand.title) != item_screen:
            continue
        if matching.similarity(item.raw_title, cand.title) >= matching.MATCH_THRESHOLD:
            cache[key] = cand
            return cand

    product = Product(
        group_key=key,
        title=item.raw_title,
        brand=brand,
        model=matching.model_core(item.raw_title, brand),
        category=item.category,
        image_url=item.image_url,
    )
    session.add(product)
    await session.flush()  # assign id
    cache[key] = product
    brand_index.setdefault(brand or "unknown", []).append(product)
    return product


async def ingest_items(session: AsyncSession, items: list[ScrapedItem]) -> list[dict]:
    """Upsert items; return a list of price/stock change events."""
    if not items:
        return []

    store_map = await _get_store_map(session)
    cache: dict[str, Product] = {}
    brand_index: dict[str, list[Product]] = {}
    changes: list[dict] = []
    now = datetime.now(timezone.utc)

    for item in items:
        store = store_map.get(item.store_slug)
        if not store:
            continue
        product = await _find_or_create_product(session, item, cache, brand_index)
        if product.image_url is None and item.image_url:
            product.image_url = item.image_url

        offer = await session.scalar(
            select(Offer).where(
                Offer.store_id == store.id, Offer.source_url == item.source_url
            )
        )

        if offer is None:
            offer = Offer(
                product_id=product.id,
                store_id=store.id,
                source_url=item.source_url,
                raw_title=item.raw_title,
                price=item.price,
                currency=item.currency,
                in_stock=item.in_stock,
                image_url=item.image_url,
                scraped_at=now,
            )
            session.add(offer)
            await session.flush()
            session.add(
                PriceHistory(offer_id=offer.id, price=item.price, in_stock=item.in_stock)
            )
            changes.append(
                {
                    "product_id": product.id,
                    "product_title": product.title,
                    "store_slug": store.slug,
                    "old_price": None,
                    "new_price": item.price,
                    "in_stock": item.in_stock,
                    "currency": item.currency,
                    "observed_at": now,
                }
            )
        else:
            price_changed = abs(offer.price - item.price) > 0.001
            stock_changed = offer.in_stock != item.in_stock
            if price_changed or stock_changed:
                old_price = offer.price
                offer.price = item.price
                offer.in_stock = item.in_stock
                offer.scraped_at = now
                session.add(
                    PriceHistory(
                        offer_id=offer.id, price=item.price, in_stock=item.in_stock
                    )
                )
                changes.append(
                    {
                        "product_id": product.id,
                        "product_title": product.title,
                        "store_slug": store.slug,
                        "old_price": old_price,
                        "new_price": item.price,
                        "in_stock": item.in_stock,
                        "currency": item.currency,
                        "observed_at": now,
                    }
                )
            else:
                offer.scraped_at = now

    await session.commit()
    return changes
