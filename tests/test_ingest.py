"""Tests for ingest: grouping, best price, and change detection."""
import pytest

from app.scrapers.base import ScrapedItem
from app.services import products as products_service
from app.services.ingest import ingest_items


def _item(store, title, price, url, brand=None):
    return ScrapedItem(store_slug=store, source_url=url, raw_title=title, price=price, brand=brand)


@pytest.mark.asyncio
async def test_same_product_groups_across_stores(session):
    items = [
        _item("kontakt", "iPhone 15 256 GB Black", 1969.99, "https://kontakt.az/iphone-15-256", "Apple"),
        _item("bakuelectronics", "Smartfon Apple iPhone 15 256GB Black", 1899.99, "https://bakuelectronics.az/mehsul/iphone-15-256"),
    ]
    await ingest_items(session, items)

    rows, total = await products_service.search_products(session, q="iphone")
    assert total == 1
    assert rows[0]["offers_count"] == 2
    assert rows[0]["best_price"] == 1899.99
    assert rows[0]["best_store"] == "bakuelectronics"


@pytest.mark.asyncio
async def test_distinct_storage_not_merged(session):
    items = [
        _item("kontakt", "iPhone 15 256 GB Black", 1969.99, "u1", "Apple"),
        _item("kontakt", "iPhone 15 128 GB Blue", 1699.99, "u2", "Apple"),
    ]
    await ingest_items(session, items)
    _, total = await products_service.search_products(session, q="iphone")
    assert total == 2


@pytest.mark.asyncio
async def test_price_change_detected(session):
    url = "https://kontakt.az/iphone-15-256"
    await ingest_items(session, [_item("kontakt", "iPhone 15 256 GB Black", 1969.99, url, "Apple")])
    changes = await ingest_items(session, [_item("kontakt", "iPhone 15 256 GB Black", 1899.99, url, "Apple")])
    assert len(changes) == 1
    assert changes[0]["old_price"] == 1969.99
    assert changes[0]["new_price"] == 1899.99


@pytest.mark.asyncio
async def test_no_change_no_event(session):
    url = "u1"
    await ingest_items(session, [_item("kontakt", "iPhone 15 256 GB", 1969.99, url, "Apple")])
    changes = await ingest_items(session, [_item("kontakt", "iPhone 15 256 GB", 1969.99, url, "Apple")])
    assert changes == []
