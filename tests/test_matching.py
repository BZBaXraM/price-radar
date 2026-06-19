"""Tests for cross-store product matching."""
from app.services import matching as m


def test_iphone_variants_collapse_across_stores():
    keys = {
        m.group_key("iPhone 15 256 GB Black", "Apple"),
        m.group_key("Smartfon Apple iPhone 15 256GB Black", None),
        m.group_key("Apple iPhone 15 256 GB qara", None),
    }
    assert len(keys) == 1, keys


def test_storage_tiers_are_distinct():
    k256 = m.group_key("iPhone 15 256 GB Black", "Apple")
    k128 = m.group_key("iPhone 15 128 GB Blue", "Apple")
    assert k256 != k128


def test_brand_extraction_apple_aliases():
    assert m.extract_brand("MacBook Air 13", None) == "apple"
    assert m.extract_brand("Smartfon Apple iPhone 15", None) == "apple"
    assert m.extract_brand("Notbuk Lenovo LOQ", "Lenovo") == "lenovo"


def test_storage_and_screen_extraction():
    assert m.extract_storage("Galaxy S25 12/256 GB") == "256gb"
    assert m.extract_storage("Laptop 1TB SSD") == "1tb"
    assert m.extract_screen('TV Samsung 55" QLED') == "55"


def test_similarity_high_for_same_product():
    assert m.similarity("iPhone 15 256 GB Black", "Apple iPhone 15 256GB") > 80
