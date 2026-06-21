"use client";

import { useEffect, useReducer } from "react";
import Link from "next/link";
import type { ProductDetail, PriceUpdate } from "@/lib/types";
import { api, WS_BASE } from "@/lib/api";
import { formatPrice, STORE_NAMES, storeColor } from "@/lib/format";
import { tr } from "@/lib/i18n";
import { useAppStore } from "@/store/useAppStore";
import { ProductImage } from "./ProductImage";

type View =
  | { status: "loading" }
  | { status: "error" }
  | { status: "ok"; data: ProductDetail };

// `syncing` = a live re-scrape is in flight; `flash` = brief "just updated" badge.
type State = { view: View; syncing: boolean; flash: boolean };

type ViewAction =
  | { type: "start" }
  | { type: "snapshot"; data: ProductDetail } // fast DB read; never clobbers live data
  | { type: "live"; data: ProductDetail }     // authoritative re-scrape result
  | { type: "live_failed" }
  | { type: "error" }
  | { type: "flash_off" }
  | { type: "patch"; change: PriceUpdate };

function reducer(state: State, action: ViewAction): State {
  switch (action.type) {
    case "start":      return { view: { status: "loading" }, syncing: true, flash: false };
    case "snapshot":   return { ...state, view: { status: "ok", data: action.data } };
    case "live":       return { view: { status: "ok", data: action.data }, syncing: false, flash: true };
    case "live_failed": return { ...state, syncing: false };
    // A failed load must not clobber prices we're already showing.
    case "error":      return state.view.status === "ok" ? state : { ...state, view: { status: "error" }, syncing: false };
    case "flash_off":  return { ...state, flash: false };
    case "patch": {
      // Live WebSocket patch: update the matching store's offer in place.
      if (state.view.status !== "ok") return state;
      const offers = state.view.data.offers.map((o) =>
        o.store_slug === action.change.store_slug
          ? { ...o, price: action.change.new_price, in_stock: action.change.in_stock }
          : o,
      );
      return { ...state, view: { status: "ok", data: { ...state.view.data, offers } } };
    }
  }
}

export function ProductDetailView({ id }: { id: number }) {
  const lang = useAppStore((s) => s.lang);
  const [{ view, syncing, flash }, dispatch] = useReducer(reducer, {
    view: { status: "loading" },
    syncing: false,
    flash: false,
  });

  // Load the product, then keep its prices live: an immediate re-scrape of the
  // stores (incl. the slow browser-backed one) on open, plus WebSocket patches
  // for background changes while the page stays open. No manual refresh button.
  useEffect(() => {
    const ctrl = new AbortController();
    let alive = true;
    let liveLoaded = false; // the live re-scrape is authoritative over the DB snapshot
    dispatch({ type: "start" });

    // 1) Fast: show the last-known (DB) snapshot right away.
    api
      .product(id, lang, ctrl.signal)
      .then((data) => { if (alive && !liveLoaded) dispatch({ type: "snapshot", data }); })
      .catch((e) => { if (alive && e.name !== "AbortError") dispatch({ type: "error" }); });

    // 2) Live: re-scrape the actual store pages and replace with real prices.
    api
      .refreshProduct(id, lang, ctrl.signal)
      .then((data) => {
        if (!alive) return;
        liveLoaded = true;
        dispatch({ type: "live", data });
        setTimeout(() => { if (alive) dispatch({ type: "flash_off" }); }, 2500);
      })
      .catch(() => { if (alive) dispatch({ type: "live_failed" }); });

    return () => { alive = false; ctrl.abort(); };
  }, [id, lang]);

  // Live price stream: patch this product's offers as background scrapes land.
  useEffect(() => {
    let closed = false;
    let retry: ReturnType<typeof setTimeout>;
    let ws: WebSocket | null = null;

    function connect() {
      if (closed) return;
      try {
        ws = new WebSocket(`${WS_BASE}/ws/prices`);
      } catch {
        retry = setTimeout(connect, 5000);
        return;
      }
      ws.onmessage = (ev) => {
        try {
          const msg = JSON.parse(ev.data);
          if (msg.type !== "price_updates" || !Array.isArray(msg.changes)) return;
          for (const change of msg.changes as PriceUpdate[]) {
            if (change.product_id === id) dispatch({ type: "patch", change });
          }
        } catch { /* ignore malformed */ }
      };
      ws.onclose = () => { if (!closed) retry = setTimeout(connect, 5000); };
      ws.onerror = () => ws?.close();
    }

    connect();
    return () => { closed = true; clearTimeout(retry); ws?.close(); };
  }, [id]);

  if (view.status === "loading") {
    return (
      <div className="max-w-6xl mx-auto px-5 py-16">
        <div className="animate-pulse grid lg:grid-cols-2 gap-12">
          <div className="aspect-square bg-paper-2" />
          <div className="space-y-4">
            <div className="h-8 bg-paper-2 w-3/4" />
            <div className="h-24 bg-paper-2" />
            <div className="h-40 bg-paper-2" />
          </div>
        </div>
      </div>
    );
  }

  if (view.status === "error") {
    return (
      <div className="max-w-6xl mx-auto px-5 py-32 text-center">
        <p className="font-display text-3xl text-muted">{tr(lang, "no_results")}</p>
        <Link href="/" className="inline-block mt-6 underline underline-offset-4 text-accent">
          {tr(lang, "back")}
        </Link>
      </div>
    );
  }

  const { data } = view;
  const offers = [...data.offers].sort((a, b) => a.price - b.price);
  const cheapest = offers[0]?.price;
  const dearest = offers[offers.length - 1]?.price;
  const savings = cheapest && dearest && dearest > cheapest ? dearest - cheapest : 0;

  return (
    <div className="max-w-6xl mx-auto px-5 py-10">
      <Link
        href="/"
        className="text-sm text-muted hover:text-ink underline underline-offset-4"
      >
        ← {tr(lang, "back")}
      </Link>

      <div className="grid lg:grid-cols-2 gap-10 lg:gap-16 mt-6">
        {/* Image */}
        <div className="group border border-line bg-paper-2 aspect-square overflow-hidden">
          <ProductImage src={data.image_url} alt={data.title} className="w-full h-full p-10" />
        </div>

        {/* Summary */}
        <div>
          {data.brand && (
            <p className="text-sm text-muted uppercase tracking-wide">{data.brand}</p>
          )}
          <h1 className="font-display text-3xl sm:text-4xl mt-2 leading-tight">{data.title}</h1>

          <div className="mt-8 border border-ink p-5">
            <p className="text-xs uppercase tracking-wide text-muted">
              {tr(lang, "best_price")}
            </p>
            <div className="flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between sm:gap-4 mt-1">
              <span className="font-display text-4xl">
                {formatPrice(cheapest, data.currency)}
              </span>
              {data.best_store && (
                <a
                  href={offers[0]?.source_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="self-start sm:self-auto bg-ink text-paper text-sm font-medium px-4 py-2.5 hover:bg-accent transition-colors"
                >
                  {tr(lang, "go_to_store")} →
                </a>
              )}
            </div>
            {savings > 0 && (
              <p className="mt-3 text-sm" style={{ color: "var(--color-deal)" }}>
                ↓ {formatPrice(savings, data.currency)} {tr(lang, "savings")}
              </p>
            )}
          </div>

          {/* Offers comparison */}
          <div className="flex items-end justify-between gap-3 mt-10 mb-3">
            <h2 className="font-display text-2xl">{tr(lang, "compare_prices")}</h2>
            <div
              className="flex items-center gap-1.5 text-xs shrink-0 whitespace-nowrap"
              aria-live="polite"
            >
              {syncing ? (
                <>
                  <span className="inline-block animate-spin" aria-hidden>↻</span>
                  <span className="text-muted">{tr(lang, "refreshing")}</span>
                </>
              ) : flash ? (
                <span style={{ color: "var(--color-deal)" }}>✓ {tr(lang, "updated_now")}</span>
              ) : (
                <>
                  <span
                    className="inline-block w-2 h-2 rounded-full animate-pulse"
                    style={{ backgroundColor: "var(--color-deal)" }}
                    aria-hidden
                  />
                  <span className="text-muted">{tr(lang, "live_prices")}</span>
                </>
              )}
            </div>
          </div>
          <div className="border border-line divide-y divide-line">
            {offers.map((o, i) => (
              <div
                key={o.id}
                className={`flex items-center justify-between gap-2 px-3 py-3 sm:gap-4 sm:px-4 ${
                  i === 0 ? "bg-paper-2" : ""
                }`}
              >
                <div className="flex items-center gap-2 min-w-0 flex-1">
                  <span
                    className="inline-block w-2 h-2 rounded-full shrink-0"
                    style={{ backgroundColor: storeColor(o.store_slug) }}
                  />
                  <div className="min-w-0">
                    <p className="text-sm font-medium truncate">
                      {STORE_NAMES[o.store_slug] ?? o.store_name}
                    </p>
                    <p
                      className={`text-xs ${
                        o.in_stock ? "text-muted" : "text-accent"
                      }`}
                    >
                      {o.in_stock_label}
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-2 sm:gap-4 shrink-0">
                  <span
                    className={`font-display text-base sm:text-lg ${i === 0 ? "text-ink" : "text-muted"}`}
                  >
                    {formatPrice(o.price, o.currency)}
                  </span>
                  <a
                    href={o.source_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-xs border border-line px-2 py-1.5 sm:px-2.5 hover:border-ink transition-colors whitespace-nowrap"
                  >
                    {tr(lang, "go_to_store")}
                  </a>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
