# PriceRadar — Backend

A price-comparison platform for products from Azerbaijani e-commerce stores
(**KontaktHome**, **İrşad**, **World Telecom**, **Baku Electronics**) with an AI assistant
for prices/products, support for 3 languages (az/ru/en), and real-time price updates.

Consists of two parts:
- **Backend** (FastAPI) — this directory `app/`.
- **Frontend** (Next.js + Bun + TailwindCSS + Zustand) — [`frontend/`](frontend/README.md) directory.

Full setup: backend on `:8000`, then `cd frontend && bun run dev` on `:3000`.

## Features

- **Scraping 4 stores** in a unified format:
  - `bakuelectronics` — Next.js `__NEXT_DATA__` JSON (httpx)
  - `irshad` — AJAX endpoint `list-products`, `.product` cards (httpx)
  - `wt` — server-rendered `.productCard` (httpx)
  - `kontakt` — behind Cloudflare → headless browser **Playwright**, parse `data-gtm` JSON
- **Pagination**:
  - Scrapers traverse multiple category pages (baku/w-t — `?page=N`, up to `SCRAPE_MAX_PAGES`);
    irshad returns entire category in one request, kontakt — rendered page.
  - REST `/api/products` supports `page` and `page_size` with `total` in response.
- **Product matching** across stores by normalized `brand|model|storage|screen`
  with fuzzy fallback (RapidFuzz); different storage sizes do not collapse.
- **Price comparison**: best price and store, all offers for a product, price history.
- **Real-time**: scheduler (APScheduler) scrapes on interval → price changes pushed
  via WebSocket `/ws/prices`.
- **AI assistant** (GLM-4.7-Flash via z.ai, OpenAI-compatible): tool-calling against DB
  (no price hallucinations), guardrail (products/prices/availability only), responds in user's language.
- **i18n**: az / ru / en (`?lang=` or `Accept-Language`).

## Setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt           # or: pip install -e ".[dev]"
playwright install chromium               # for kontakt.az scraper
cp glm-4.7-flash-api-intregration.txt .env  # already created; contains ZAI_*
uvicorn app.main:app --reload
```

Open Swagger: http://127.0.0.1:8000/docs

## Configuration (`.env`)

| Variable | Default | Description |
|---|---|---|
| `ZAI_API_KEY` / `ZAI_MODEL` / `ZAI_BASE_URL` | — | access to GLM (z.ai) |
| `DATABASE_URL` | `sqlite+aiosqlite:///./price_radar.db` | Database |
| `SCRAPE_INTERVAL_MIN` | `30` | scheduler interval |
| `SCRAPE_LIMIT_PER_STORE` | `60` | product limit per run |
| `SCRAPE_MAX_PAGES` | `5` | max category pages for pagination (baku/w-t) |
| `SCRAPE_ENABLED` | `true` | auto-scrape on startup (`false` — disable) |

## API

| Method | Path | Description |
|---|---|---|
| GET | `/health` | health check |
| GET | `/api/products?q=&category=&brand=&store=&min_price=&max_price=&sort=&page=&lang=` | search with best price |
| GET | `/api/products/{id}?lang=` | product card + all offers by store |
| GET | `/api/stores` | store list and last scrape status |
| POST | `/api/admin/scrape/{store}` | manual scrape (`kontakt`/`irshad`/`wt`/`bakuelectronics`/`all`) |
| POST | `/api/chat` | AI assistant (`{message, lang, history}`) |
| WS | `/ws/chat` | AI assistant via WebSocket |
| WS | `/ws/prices` | real-time price change pushes |

## Tests

```bash
pytest        # offline tests for scrapers on fixtures + matching + ingest + AI tools
```

## Structure

```
app/
  main.py            entry point, lifespan (DB + scheduler), CORS
  config.py          settings (pydantic-settings)
  database.py        async SQLAlchemy, init_db, seed_stores
  models.py          Store, Product, Offer, PriceHistory
  schemas.py         Pydantic schemas
  i18n.py            dictionaries az/ru/en
  deps.py            get_db, get_lang
  scrapers/          base, http_client, browser (Playwright), 4 stores, registry
  services/          matching, ingest, products, scheduler, ws_manager, ai_assistant
  routers/           products, stores, chat, prices, health
tests/               matching, scrapers (fixtures), ingest, AI guardrails
```

## Production Notes
- Database: currently **SQLite** (sufficient for current stage).
- For robust production scraping — proxy pool/anti-ban (especially kontakt/Cloudflare).
- Respect robots.txt and store ToS; scraping with reasonable limits/intervals.