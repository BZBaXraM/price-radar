"""Pytest fixtures: in-memory DB with seeded stores."""
from __future__ import annotations

import pathlib
from collections.abc import AsyncIterator

import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.database import Base
from app.models import Store
from app.scrapers.registry import STORE_DEFS

FIXTURES = pathlib.Path(__file__).parent / "fixtures"


def load_fixture(name: str) -> str:
    return (FIXTURES / name).read_text()


@pytest_asyncio.fixture
async def session() -> AsyncIterator[AsyncSession]:
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with maker() as s:
        for slug, meta in STORE_DEFS.items():
            s.add(Store(slug=slug, name=meta["name"], base_url=meta["base_url"],
                        requires_browser=meta["requires_browser"], active=True))
        await s.commit()
        yield s
    await engine.dispose()
