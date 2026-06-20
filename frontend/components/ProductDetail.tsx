"use client";

import { useCallback, useEffect, useReducer, useState } from "react";
import Link from "next/link";
import type { ProductDetail } from "@/lib/types";
import { api } from "@/lib/api";
import { formatPrice, STORE_NAMES, storeColor } from "@/lib/format";
import { tr } from "@/lib/i18n";
import { useAppStore } from "@/store/useAppStore";
import { ProductImage } from "./ProductImage";

type ViewState =
  | { status: "loading" }
  | { status: "error" }
  | { status: "ok"; data: ProductDetail };

type ViewAction =
  | { type: "start" }
  | { type: "success"; data: ProductDetail }
  | { type: "error" };

function reducer(_: ViewState, action: ViewAction): ViewState {
  switch (action.type) {
    case "start":  return { status: "loading" };
    case "success": return { status: "ok", data: action.data };
    case "error":  return { status: "error" };
  }
}

export function ProductDetailView({ id }: { id: number }) {
  const lang = useAppStore((s) => s.lang);
  const [state, dispatch] = useReducer(reducer, { status: "loading" });
  const [refreshing, setRefreshing] = useState(false);
  const [flash, setFlash] = useState(false);

  const onRefresh = useCallback(async () => {
    setRefreshing(true);
    try {
      const data = await api.refreshProduct(id, lang);
      dispatch({ type: "success", data });
      setFlash(true);
      setTimeout(() => setFlash(false), 2500);
    } catch {
      /* keep current data on failure */
    } finally {
      setRefreshing(false);
    }
  }, [id, lang]);

  useEffect(() => {
    const ctrl = new AbortController();
    let alive = true;
    dispatch({ type: "start" });

    api
      .product(id, lang, ctrl.signal)
      .then((data) => { if (alive) dispatch({ type: "success", data }); })
      .catch((e) => { if (alive && e.name !== "AbortError") dispatch({ type: "error" }); });

    return () => { alive = false; ctrl.abort(); };
  }, [id, lang]);

  if (state.status === "loading") {
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

  if (state.status === "error") {
    return (
      <div className="max-w-6xl mx-auto px-5 py-32 text-center">
        <p className="font-display text-3xl text-muted">{tr(lang, "no_results")}</p>
        <Link href="/" className="inline-block mt-6 underline underline-offset-4 text-accent">
          {tr(lang, "back")}
        </Link>
      </div>
    );
  }

  const { data } = state;
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
            <div className="flex items-center gap-2 shrink-0">
              {flash && (
                <span className="text-xs" style={{ color: "var(--color-deal)" }}>
                  ✓ {tr(lang, "updated_now")}
                </span>
              )}
              <button
                type="button"
                onClick={onRefresh}
                disabled={refreshing}
                aria-busy={refreshing}
                className="inline-flex items-center gap-1.5 text-xs border border-line px-2.5 py-1.5 hover:border-ink transition-colors disabled:opacity-50 disabled:cursor-not-allowed whitespace-nowrap"
              >
                <span className={`inline-block ${refreshing ? "animate-spin" : ""}`} aria-hidden>
                  ↻
                </span>
                {refreshing ? tr(lang, "refreshing") : tr(lang, "refresh_price")}
              </button>
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
