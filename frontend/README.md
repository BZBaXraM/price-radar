# PriceRadar — Frontend

Next.js (App Router) + Bun + TailwindCSS v4 + Zustand. Phase 2 of the PriceRadar project.
Connects to FastAPI backend (phase 1) for catalog, price comparison, AI chat, and real-time.

## Features

- **Catalog** with search, filters (store, sort, price range), and **pagination**.
- **Beautiful product cards** with images (editorial grayscale→color on hover), badges for
  offer count and brand.
- **Product page** — price comparison across all stores, best price highlight, savings calculation,
  store redirect buttons.
- **AI assistant** (floating chat) — questions about prices/products, answers in interface language.
- **3 languages** (az/ru/en) with instant switching (Zustand + localStorage).
- **Real-time** — toasts for price changes via WebSocket `/ws/prices`.

## Design

Editorial system (per `../prompts/DESIGN-UI-SYSTEM-prompt.md`): **no purple/violet**,
warm off-white background, ink black, single accent — burnt orange. Fonts: **Fraunces**
(headings, serif) + **Inter** (text). Borders instead of shadows, subtle hover transitions.

## Setup

```bash
bun install
# .env.local already created:
#   NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
#   NEXT_PUBLIC_WS_URL=ws://127.0.0.1:8000
bun run dev            # http://localhost:3000  (backend must run on :8000)
bun run build && bun run start   # production
```

## Structure

```
app/
  layout.tsx              fonts, Header, Footer, ChatWidget, LivePriceToaster
  page.tsx                home: Hero + Catalog (in Suspense)
  product/[id]/page.tsx   product page (params — Promise, via use())
  globals.css             Tailwind v4 design system (@theme)
components/
  Header, LanguageSwitcher, Hero, Catalog, Filters, Pagination,
  ProductCard, ProductImage, StoreBadge, ProductDetail, Skeleton,
  ChatWidget, LivePriceToaster
lib/
  api.ts     FastAPI client + WS base
  types.ts   types (Product/Offer/...)
  i18n.ts    dictionaries az/ru/en + tr()
  format.ts  price format, store colors/names
store/
  useAppStore.ts  Zustand (language, chat state)
```

> Note: Next 16 — `params` for dynamic routes are async; `useSearchParams`
> wrapped in `Suspense` (including in layout for prerender compatibility with `/_not-found`).
