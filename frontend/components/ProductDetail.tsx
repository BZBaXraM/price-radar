"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import type { ProductDetail } from "@/lib/types";
import { api } from "@/lib/api";
import { formatPrice, STORE_NAMES, storeColor } from "@/lib/format";
import { tr } from "@/lib/i18n";
import { useAppStore } from "@/store/useAppStore";
import { ProductImage } from "./ProductImage";
import { StoreBadge } from "./StoreBadge";

export function ProductDetailView({ id }: { id: number }) {
  const lang = useAppStore((s) => s.lang);
  const [data, setData] = useState<ProductDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [notFound, setNotFound] = useState(false);

  useEffect(() => {
    const ctrl = new AbortController();
    setLoading(true);
    setNotFound(false);
    api
      .product(id, lang, ctrl.signal)
      .then(setData)
      .catch((e) => {
        if (e.name !== "AbortError") setNotFound(true);
      })
      .finally(() => setLoading(false));
    return () => ctrl.abort();
  }, [id, lang]);

  if (loading) {
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

  if (notFound || !data) {
    return (
      <div className="max-w-6xl mx-auto px-5 py-32 text-center">
        <p className="font-display text-3xl text-muted">{tr(lang, "no_results")}</p>
        <Link href="/" className="inline-block mt-6 underline underline-offset-4 text-accent">
          {tr(lang, "back")}
        </Link>
      </div>
    );
  }

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
            <div className="flex items-end justify-between gap-4 mt-1">
              <span className="font-display text-4xl">
                {formatPrice(cheapest, data.currency)}
              </span>
              {data.best_store && (
                <a
                  href={offers[0]?.source_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="bg-ink text-paper text-sm font-medium px-4 py-2.5 hover:bg-accent transition-colors"
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
          <h2 className="font-display text-2xl mt-10 mb-3">{tr(lang, "compare_prices")}</h2>
          <div className="border border-line divide-y divide-line">
            {offers.map((o, i) => (
              <div
                key={o.id}
                className={`flex items-center justify-between gap-4 px-4 py-3 ${
                  i === 0 ? "bg-paper-2" : ""
                }`}
              >
                <div className="flex items-center gap-3 min-w-0">
                  <span
                    className="inline-block w-2.5 h-2.5 rounded-full shrink-0"
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
                <div className="flex items-center gap-4 shrink-0">
                  <span
                    className={`font-display text-lg ${i === 0 ? "text-ink" : "text-muted"}`}
                  >
                    {formatPrice(o.price, o.currency)}
                  </span>
                  <a
                    href={o.source_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-xs border border-line px-2.5 py-1.5 hover:border-ink transition-colors whitespace-nowrap"
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
