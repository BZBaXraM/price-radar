"""Tests for on-demand single-product refresh."""
import pytest

from app.scrapers.base import OfferSnapshot
from app.services import refresh as refresh_svc
from app.services.ingest import ingest_items
from app.scrapers.base import ScrapedItem


class _FakeScraper:
    """Returns a preset snapshot per source_url; mimics requires_browser stores."""

    def __init__(self, snapshots, requires_browser=False):
        self._snapshots = snapshots
        self.requires_browser = requires_browser

    async def fetch_offer(self, url):
        return self._snapshots.get(url)


async def _seed(session):
    await ingest_items(
        session,
        [
            ScrapedItem(store_slug="wt", source_url="https://w-t.az/iphone-15+p1",
                        raw_title="iPhone 15 256 GB", price=2000.0),
            ScrapedItem(store_slug="bakuelectronics",
                        source_url="https://bakuelectronics.az/mehsul/iphone-15-256",
                        raw_title="Apple iPhone 15 256GB", price=1950.0),
        ],
    )
    from app.services import products as products_service
    rows, _ = await products_service.search_products(session, q="iphone")
    return rows[0]["id"]


@pytest.mark.asyncio
async def test_refresh_updates_price_and_emits_change(session, monkeypatch):
    pid = await _seed(session)
    snaps = {
        "https://w-t.az/iphone-15+p1": OfferSnapshot(price=1899.0, in_stock=True),
        "https://bakuelectronics.az/mehsul/iphone-15-256": OfferSnapshot(price=1950.0, in_stock=True),
    }
    monkeypatch.setattr(refresh_svc, "get_scraper", lambda slug: _FakeScraper(snaps))

    result = await refresh_svc.refresh_product(session, pid)

    assert result["status"] == "ok"
    assert result["checked"] == 2
    assert result["refreshed"] == 2
    # only the wt offer changed (2000 -> 1899)
    assert len(result["changes"]) == 1
    ch = result["changes"][0]
    assert ch["old_price"] == 2000.0
    assert ch["new_price"] == 1899.0
    assert ch["store_slug"] == "wt"

    from app.services import products as products_service
    detail = await products_service.get_product_detail(session, pid)
    assert detail["best_price"] == 1899.0


@pytest.mark.asyncio
async def test_refresh_skips_browser_stores_by_default(session, monkeypatch):
    pid = await _seed(session)
    # both offers point at a browser-backed fake; with include_slow=False none run
    monkeypatch.setattr(
        refresh_svc, "get_scraper",
        lambda slug: _FakeScraper({}, requires_browser=True),
    )
    # mark the seeded stores as browser-backed for this product
    from sqlalchemy import update
    from app.models import Store
    await session.execute(update(Store).values(requires_browser=True))
    await session.commit()

    result = await refresh_svc.refresh_product(session, pid)
    assert result["checked"] == 0
    assert result["changes"] == []


@pytest.mark.asyncio
async def test_refresh_missing_product_returns_none(session):
    assert await refresh_svc.refresh_product(session, 99999) is None
