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
