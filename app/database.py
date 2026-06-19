"""Async SQLAlchemy engine, session factory and Base."""
from __future__ import annotations

from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.config import settings

engine = create_async_engine(settings.database_url, echo=False, future=True)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def init_db() -> None:
    """Create tables (and seed stores) on startup."""
    from app import models  # noqa: F401  (register mappers)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await seed_stores()


async def seed_stores() -> None:
    from sqlalchemy import select

    from app.models import Store
    from app.scrapers.registry import STORE_DEFS

    async with async_session() as session:
        existing = {s.slug for s in (await session.scalars(select(Store))).all()}
        for slug, meta in STORE_DEFS.items():
            if slug not in existing:
                session.add(
                    Store(
                        slug=slug,
                        name=meta["name"],
                        base_url=meta["base_url"],
                        requires_browser=meta["requires_browser"],
                        active=True,
                    )
                )
        await session.commit()


async def get_db() -> AsyncIterator[AsyncSession]:
    async with async_session() as session:
        yield session
