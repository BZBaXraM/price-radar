"""Offline parser tests using saved HTML fixtures."""
from app.scrapers.bakuelectronics import BakuElectronicsScraper
from app.scrapers.irshad import IrshadScraper
from app.scrapers.kontakt import KontaktScraper
from app.scrapers.wt import WorldTelecomScraper
from tests.conftest import load_fixture


def _assert_items(items, slug):
    assert items, f"{slug} produced no items"
    for it in items[:5]:
        assert it.store_slug == slug
        assert it.raw_title
        assert it.price and it.price > 0
        assert it.source_url.startswith("http")


def test_baku_parse():
    items = BakuElectronicsScraper.parse(load_fixture("baku_category.html"), category="noutbuklar")
    _assert_items(items, "bakuelectronics")


def test_irshad_parse():
    items = IrshadScraper.parse_cards(load_fixture("irshad_listproducts.html"), category="fotoaparatlar")
    _assert_items(items, "irshad")


def test_wt_parse():
    items = WorldTelecomScraper.parse_cards(load_fixture("wt_category.html"), category="telefon")
    _assert_items(items, "wt")


def test_kontakt_parse():
    items = KontaktScraper.parse_cards(load_fixture("kontakt_home.html"))
    _assert_items(items, "kontakt")
    # kontakt data-gtm carries brand info
    assert any(it.brand for it in items)


# --- single-product detail parsers (on-demand refresh) ---

def test_baku_parse_detail():
    snap = BakuElectronicsScraper.parse_detail(load_fixture("baku_detail.html"))
    assert snap is not None
    assert snap.price > 0
    assert snap.in_stock is True


def test_wt_parse_detail():
    snap = WorldTelecomScraper.parse_detail(load_fixture("wt_detail.html"))
    assert snap is not None
    assert snap.price > 0
    assert snap.in_stock is True


def test_irshad_parse_detail():
    snap = IrshadScraper.parse_detail(load_fixture("irshad_detail.html"))
    assert snap is not None
    assert snap.price > 0


def test_parse_detail_handles_garbage():
    assert WorldTelecomScraper.parse_detail("<html></html>") is None
    assert BakuElectronicsScraper.parse_detail("<html></html>") is None
    assert IrshadScraper.parse_detail("<html></html>") is None
