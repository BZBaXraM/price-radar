"use client";

import { useEffect, useReducer, useState } from "react";
import { useSearchParams } from "next/navigation";
import { api } from "@/lib/api";
import type { ProductSummary } from "@/lib/types";
import { tr } from "@/lib/i18n";
import { useAppStore } from "@/store/useAppStore";
import { ProductCard } from "./ProductCard";
import { Filters, DEFAULT_FILTERS, type FilterState } from "./Filters";
import { Pagination } from "./Pagination";
import { GridSkeleton } from "./Skeleton";

const PAGE_SIZE = 20;

type FetchState = {
  items: ProductSummary[];
  total: number;
  loading: boolean;
  error: boolean;
};

type FetchAction =
  | { type: "start" }
  | { type: "success"; items: ProductSummary[]; total: number }
  | { type: "error" };

function fetchReducer(state: FetchState, action: FetchAction): FetchState {
  switch (action.type) {
    case "start":
      return { ...state, loading: true, error: false };
    case "success":
      return { items: action.items, total: action.total, loading: false, error: false };
    case "error":
      return { items: [], total: 0, loading: false, error: true };
  }
}

// Unified query state — single source of truth for the current fetch.
type QueryState = {
  q: string;
  filters: FilterState;
  page: number;
};

export function Catalog() {
  const lang = useAppStore((s) => s.lang);
  const params = useSearchParams();
  const urlQ = params.get("q") ?? "";

  const [query, setQuery] = useState<QueryState>({
    q: urlQ,
    filters: DEFAULT_FILTERS,
    page: 1,
  });

  const [{ items, total, loading, error }, dispatch] = useReducer(fetchReducer, {
    items: [],
    total: 0,
    loading: true,
    error: false,
  });

  // "Storing information from previous renders" — React-recommended pattern for syncing
  // derived state when an external input (URL) changes without using an effect.
  // React re-renders immediately with the updated query when urlQ diverges.
  if (query.q !== urlQ) {
    setQuery((prev) => ({ ...prev, q: urlQ, page: 1 }));
  }

  useEffect(() => {
    const ctrl = new AbortController();
    let alive = true;
    dispatch({ type: "start" });

    api
      .products(
        {
          q: query.q || undefined,
          store: query.filters.store || undefined,
          sort: query.filters.sort,
          min_price: query.filters.min_price ? Number(query.filters.min_price) : undefined,
          max_price: query.filters.max_price ? Number(query.filters.max_price) : undefined,
          page: query.page,
          page_size: PAGE_SIZE,
          lang,
        },
        ctrl.signal,
      )
      .then((res) => {
        if (!alive) return;
        dispatch({ type: "success", items: res.items, total: res.total });
      })
      .catch((e) => {
        if (!alive || e.name === "AbortError") return;
        dispatch({ type: "error" });
      });

    return () => {
      alive = false;
      ctrl.abort();
    };
  }, [query, lang]);

  function handleFiltersChange(filters: FilterState) {
    setQuery((prev) => ({ ...prev, filters, page: 1 }));
  }

  function handlePageChange(page: number) {
    setQuery((prev) => ({ ...prev, page }));
  }

  return (
    <section className="max-w-6xl mx-auto px-5 py-12">
      <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-4 mb-8">
        <div>
          <h2 className="font-display text-3xl">
            {urlQ ? `"${urlQ}"` : tr(lang, "featured")}
          </h2>
          <p className="text-sm text-muted mt-1">
            {loading ? tr(lang, "loading") : `${total} ${tr(lang, "results")}`}
          </p>
        </div>
        <Filters value={query.filters} onChange={handleFiltersChange} />
      </div>

      {loading ? (
        <GridSkeleton count={PAGE_SIZE} />
      ) : error ? (
        <div className="py-24 text-center">
          <p className="font-display text-2xl text-muted">{tr(lang, "no_results")}</p>
          <p className="text-sm text-accent mt-2">API əlaqəsi kəsildi. Yenidən cəhd edin.</p>
        </div>
      ) : items.length === 0 ? (
        <div className="py-24 text-center">
          <p className="font-display text-2xl text-muted">{tr(lang, "no_results")}</p>
        </div>
      ) : (
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-4">
          {items.map((p, i) => (
            <div key={p.id} className="animate-fade-up" style={{ animationDelay: `${i * 60}ms` }}>
              <ProductCard p={p} />
            </div>
          ))}
        </div>
      )}

      <Pagination page={query.page} pageSize={PAGE_SIZE} total={total} onPage={handlePageChange} />
    </section>
  );
}
