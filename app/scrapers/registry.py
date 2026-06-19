"""Store metadata, curated category lists, and scraper registry."""
from __future__ import annotations

# Curated MVP category sets per store. Kept small to avoid hammering sites;
# expand later. Paths are relative to each store's base_url.
CATEGORIES: dict[str, list[str]] = {
    "bakuelectronics": [
        "/catalog/telefonlar-plansetler",
        "/catalog/noutbuklar-komputerler-planshetler/noutbuklar",
        "/catalog/boyuk-meiset-texnikasi/soyuducular",
        "/catalog/boyuk-meiset-texnikasi/paltaryuyan-masinlar",
    ],
    # irshad: category landing pages; scraper resolves the list-products endpoint.
    "irshad": [
        "/az/telefon-ve-aksesuarlar",
        "/az/notbuk-planset-ve-komputer-texnikasi",
        "/az/foto-texnika/fotoaparatlar",
        "/az/boyuk-meiset-texnikasi",
    ],
    "wt": [
        "/k1+telefon-plansetler-saat",
        "/k4+noutbuk-komputer-ofis",
        "/k5+tv-audio-foto",
    ],
    # kontakt: handled via rendered homepage product sliders (Cloudflare).
    "kontakt": [
        "/",
    ],
}

STORE_DEFS: dict[str, dict] = {
    "kontakt": {
        "name": "KontaktHome",
        "base_url": "https://kontakt.az",
        "requires_browser": True,
    },
    "irshad": {
        "name": "İrşad Electronics",
        "base_url": "https://irshad.az",
        "requires_browser": False,
    },
    "wt": {
        "name": "World Telecom",
        "base_url": "https://w-t.az",
        "requires_browser": False,
    },
    "bakuelectronics": {
        "name": "Baku Electronics",
        "base_url": "https://bakuelectronics.az",
        "requires_browser": False,
    },
}


def get_scraper(slug: str):
    """Lazy import to avoid loading Playwright unless needed."""
    from app.scrapers.bakuelectronics import BakuElectronicsScraper
    from app.scrapers.irshad import IrshadScraper
    from app.scrapers.kontakt import KontaktScraper
    from app.scrapers.wt import WorldTelecomScraper

    mapping = {
        "kontakt": KontaktScraper,
        "irshad": IrshadScraper,
        "wt": WorldTelecomScraper,
        "bakuelectronics": BakuElectronicsScraper,
    }
    cls = mapping.get(slug)
    return cls() if cls else None
