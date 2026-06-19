"""Read-side product queries shared by REST routers and the AI assistant."""
from __future__ import annotations

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Offer, Product, Store


def _best(offers: list[Offer]) -> tuple[float | None, str | None]:
    in_stock = [o for o in offers if o.in_stock] or offers
    if not in_stock:
        return None, None
    best = min(in_stock, key=lambda o: o.price)
    return best.price, best.store.slug if best.store else None


async def search_products(
    session: AsyncSession,
    q: str | None = None,
    category: str | None = None,
    brand: str | None = None,
    store: str | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    sort: str = "relevance",
    page: int = 1,
    page_size: int = 24,
) -> tuple[list[dict], int]:
    stmt = select(Product).options(selectinload(Product.offers).selectinload(Offer.store))

    if q:
        like = f"%{q.lower()}%"
        stmt = stmt.where(or_(func.lower(Product.title).like(like), func.lower(Product.brand).like(like)))
    if category:
        stmt = stmt.where(func.lower(Product.category) == category.lower())
    if brand:
        stmt = stmt.where(func.lower(Product.brand) == brand.lower())

    products = (await session.scalars(stmt)).all()

    rows: list[dict] = []
    for p in products:
        offers = p.offers
        if store:
            offers = [o for o in offers if o.store and o.store.slug == store]
        if not offers:
            continue
        best_price, best_store = _best(offers)
        if best_price is None:
            continue
        if min_price is not None and best_price < min_price:
            continue
        if max_price is not None and best_price > max_price:
            continue
        rows.append(
            {
                "id": p.id,
                "title": p.title,
                "brand": p.brand,
                "model": p.model,
                "category": p.category,
                "image_url": p.image_url,
                "best_price": best_price,
                "best_store": best_store,
                "currency": offers[0].currency if offers else "AZN",
                "offers_count": len(offers),
            }
        )

    if sort == "price_asc":
        rows.sort(key=lambda r: r["best_price"])
    elif sort == "price_desc":
        rows.sort(key=lambda r: r["best_price"], reverse=True)
    elif sort == "offers":
        rows.sort(key=lambda r: r["offers_count"], reverse=True)

    total = len(rows)
    start = (page - 1) * page_size
    return rows[start : start + page_size], total


async def get_product_detail(session: AsyncSession, product_id: int) -> dict | None:
    p = await session.scalar(
        select(Product)
        .where(Product.id == product_id)
        .options(selectinload(Product.offers).selectinload(Offer.store))
    )
    if not p:
        return None
    offers = sorted(p.offers, key=lambda o: o.price)
    best_price, best_store = _best(p.offers)
    return {
        "id": p.id,
        "title": p.title,
        "brand": p.brand,
        "model": p.model,
        "category": p.category,
        "image_url": p.image_url,
        "best_price": best_price,
        "best_store": best_store,
        "currency": offers[0].currency if offers else "AZN",
        "offers_count": len(offers),
        "offers": [
            {
                "id": o.id,
                "store_slug": o.store.slug if o.store else "",
                "store_name": o.store.name if o.store else "",
                "source_url": o.source_url,
                "price": o.price,
                "currency": o.currency,
                "in_stock": o.in_stock,
                "image_url": o.image_url,
                "scraped_at": o.scraped_at,
            }
            for o in offers
        ],
    }


async def list_stores(session: AsyncSession) -> list[Store]:
    return list((await session.scalars(select(Store))).all())
