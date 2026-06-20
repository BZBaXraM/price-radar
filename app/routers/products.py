"""Product search and detail endpoints."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.deps import get_db, get_lang
from app.i18n import t
from app.schemas import ProductDetail, ProductListResponse
from app.services import products as svc

router = APIRouter(prefix="/api/products", tags=["products"])


def _localize_detail(detail: dict, lang: str) -> dict:
    for o in detail["offers"]:
        o["in_stock_label"] = t("in_stock" if o["in_stock"] else "out_of_stock", lang)
    if detail.get("category"):
        detail["category_label"] = t(detail["category"].lower(), lang)
    return detail


@router.get("", response_model=ProductListResponse)
async def list_products(
    q: str | None = None,
    category: str | None = None,
    brand: str | None = None,
    store: str | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    sort: str = Query("relevance", pattern="^(relevance|price_asc|price_desc|offers)$"),
    page: int = Query(1, ge=1),
    page_size: int = Query(24, ge=1, le=100),
    lang: str = Depends(get_lang),
    db: AsyncSession = Depends(get_db),
):
    rows, total = await svc.search_products(
        db, q=q, category=category, brand=brand, store=store,
        min_price=min_price, max_price=max_price, sort=sort,
        page=page, page_size=page_size,
    )
    for row in rows:
        if row.get("category"):
            row["category_label"] = t(row["category"].lower(), lang)
    return {"items": rows, "total": total, "page": page, "page_size": page_size}


@router.get("/{product_id}", response_model=ProductDetail)
async def product_detail(
    product_id: int,
    lang: str = Depends(get_lang),
    db: AsyncSession = Depends(get_db),
):
    detail = await svc.get_product_detail(db, product_id)
    if not detail:
        raise HTTPException(status_code=404, detail="Product not found")
    return _localize_detail(detail, lang)


@router.post("/{product_id}/refresh", response_model=ProductDetail)
async def refresh_product(
    product_id: int,
    include_slow: bool = Query(False, description="Also refresh browser-backed stores (kontakt; slow)"),
    lang: str = Depends(get_lang),
    db: AsyncSession = Depends(get_db),
):
    """On-demand re-scrape of just this product's offers; returns fresh detail.

    Changed prices are also broadcast over ``/ws/prices`` like scheduled runs.
    """
    from app.services.refresh import refresh_product as do_refresh

    result = await do_refresh(db, product_id, include_slow=include_slow)
    if result is None:
        raise HTTPException(status_code=404, detail="Product not found")
    detail = await svc.get_product_detail(db, product_id)
    if not detail:
        raise HTTPException(status_code=404, detail="Product not found")
    return _localize_detail(detail, lang)
