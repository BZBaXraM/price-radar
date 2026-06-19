"""Pydantic schemas for API responses and requests."""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class StoreOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    slug: str
    name: str
    base_url: str
    requires_browser: bool
    active: bool
    last_scraped_at: datetime | None = None
    last_status: str | None = None


class OfferOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    store_slug: str
    store_name: str
    source_url: str
    price: float
    currency: str
    in_stock: bool
    in_stock_label: str
    image_url: str | None = None
    scraped_at: datetime


class ProductSummary(BaseModel):
    id: int
    title: str
    brand: str | None = None
    model: str | None = None
    category: str | None = None
    image_url: str | None = None
    best_price: float | None = None
    best_store: str | None = None
    currency: str = "AZN"
    offers_count: int = 0


class ProductDetail(ProductSummary):
    offers: list[OfferOut] = Field(default_factory=list)


class ProductListResponse(BaseModel):
    items: list[ProductSummary]
    total: int
    page: int
    page_size: int


class ChatRequest(BaseModel):
    message: str
    lang: str = "az"
    history: list[dict[str, str]] = Field(default_factory=list)


class ChatResponse(BaseModel):
    reply: str
    lang: str
    used_products: list[ProductSummary] = Field(default_factory=list)


class PriceUpdateEvent(BaseModel):
    product_id: int
    product_title: str
    store_slug: str
    old_price: float | None
    new_price: float
    in_stock: bool
    currency: str = "AZN"
    observed_at: datetime
