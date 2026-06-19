"""SQLAlchemy ORM models for PriceRadar."""
from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Store(Base):
    __tablename__ = "stores"

    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(40), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(120))
    base_url: Mapped[str] = mapped_column(String(255))
    requires_browser: Mapped[bool] = mapped_column(Boolean, default=False)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    last_scraped_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_status: Mapped[str | None] = mapped_column(String(255), nullable=True)

    offers: Mapped[list["Offer"]] = relationship(back_populates="store")


class Product(Base):
    """Canonical product — groups offers from multiple stores."""

    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)
    group_key: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    title: Mapped[str] = mapped_column(String(512))
    brand: Mapped[str | None] = mapped_column(String(80), index=True, nullable=True)
    model: Mapped[str | None] = mapped_column(String(160), nullable=True)
    category: Mapped[str | None] = mapped_column(String(80), index=True, nullable=True)
    image_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    offers: Mapped[list["Offer"]] = relationship(
        back_populates="product", cascade="all, delete-orphan"
    )


class Offer(Base):
    """A single store's listing of a product."""

    __tablename__ = "offers"
    __table_args__ = (UniqueConstraint("store_id", "source_url", name="uq_store_url"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id", ondelete="CASCADE"), index=True)
    store_id: Mapped[int] = mapped_column(ForeignKey("stores.id"), index=True)
    source_url: Mapped[str] = mapped_column(String(1024))
    raw_title: Mapped[str] = mapped_column(String(512))
    price: Mapped[float] = mapped_column(Float, index=True)
    currency: Mapped[str] = mapped_column(String(8), default="AZN")
    in_stock: Mapped[bool] = mapped_column(Boolean, default=True)
    image_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    scraped_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow
    )

    product: Mapped["Product"] = relationship(back_populates="offers")
    store: Mapped["Store"] = relationship(back_populates="offers")
    history: Mapped[list["PriceHistory"]] = relationship(
        back_populates="offer", cascade="all, delete-orphan"
    )


class PriceHistory(Base):
    __tablename__ = "price_history"

    id: Mapped[int] = mapped_column(primary_key=True)
    offer_id: Mapped[int] = mapped_column(ForeignKey("offers.id", ondelete="CASCADE"), index=True)
    price: Mapped[float] = mapped_column(Float)
    in_stock: Mapped[bool] = mapped_column(Boolean, default=True)
    observed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), default=_utcnow
    )

    offer: Mapped["Offer"] = relationship(back_populates="history")
