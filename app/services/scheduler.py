"""Background scraping scheduler.

Runs each active store's scraper on an interval, ingests results, and pushes
price changes to connected WebSocket clients. A per-store lock prevents
overlapping runs (Playwright runs can be slow).
"""
from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy import select

from app.config import settings
from app.database import async_session
from app.models import Store
from app.scrapers.registry import get_scraper
from app.services.ingest import ingest_items
from app.services.ws_manager import price_manager

log = logging.getLogger("price_radar.scheduler")

_scheduler: AsyncIOScheduler | None = None
_locks: dict[str, asyncio.Lock] = {}


async def scrape_store(slug: str) -> dict:
    """Scrape a single store, ingest, broadcast changes. Returns a summary."""
    lock = _locks.setdefault(slug, asyncio.Lock())
    if lock.locked():
        return {"store": slug, "status": "skipped (already running)"}

    async with lock:
        scraper = get_scraper(slug)
        if scraper is None:
            return {"store": slug, "status": "no scraper"}

        status = "ok"
        items = []
        try:
            items = await scraper.run(limit=settings.scrape_limit_per_store)
        except Exception as exc:  # graceful degradation per store
            status = f"error: {exc}"
            log.warning("Scrape failed for %s: %s", slug, exc)

        changes: list[dict] = []
        if items:
            async with async_session() as session:
                changes = await ingest_items(session, items)

        # Update store status.
        async with async_session() as session:
            store = await session.scalar(select(Store).where(Store.slug == slug))
            if store:
                store.last_scraped_at = datetime.now(timezone.utc)
                store.last_status = f"{status}; {len(items)} items"
                await session.commit()

        await price_manager.broadcast_changes(changes)
        return {
            "store": slug,
            "status": status,
            "items": len(items),
            "changes": len(changes),
        }


async def scrape_all() -> list[dict]:
    async with async_session() as session:
        slugs = [
            s.slug
            for s in (await session.scalars(select(Store).where(Store.active.is_(True)))).all()
        ]
    return [await scrape_store(slug) for slug in slugs]


def start_scheduler() -> None:
    global _scheduler
    if not settings.scrape_enabled or _scheduler is not None:
        return
    _scheduler = AsyncIOScheduler(timezone="UTC")
    _scheduler.add_job(
        scrape_all,
        "interval",
        minutes=settings.scrape_interval_min,
        id="scrape_all",
        next_run_time=datetime.now(timezone.utc),  # run once shortly after startup
        max_instances=1,
        coalesce=True,
    )
    _scheduler.start()
    log.info("Scheduler started (every %s min)", settings.scrape_interval_min)


def stop_scheduler() -> None:
    global _scheduler
    if _scheduler is not None:
        _scheduler.shutdown(wait=False)
        _scheduler = None
