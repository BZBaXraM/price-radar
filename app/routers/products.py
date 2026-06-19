"""Product search and detail endpoints."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.deps import get_db, get_lang
from app.i18n import t
from app.schemas import ProductDetail, ProductListResponse
from app.services import products as svc

router = APIRouter(prefix="/api/products", tags=["products"])


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
    for o in detail["offers"]:
        o["in_stock_label"] = t("in_stock" if o["in_stock"] else "out_of_stock", lang)
    return detail
