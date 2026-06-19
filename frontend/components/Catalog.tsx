"use client";

import { useEffect, useState } from "react";
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

export function Catalog() {
  const lang = useAppStore((s) => s.lang);
  const params = useSearchParams();
  const q = params.get("q") ?? "";

  const [filters, setFilters] = useState<FilterState>(DEFAULT_FILTERS);
  const [page, setPage] = useState(1);
  const [items, setItems] = useState<ProductSummary[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);

  // Reset to page 1 whenever the query or filters change.
  useEffect(() => {
    setPage(1);
  }, [q, filters]);

  useEffect(() => {
    const ctrl = new AbortController();
    setLoading(true);
    api
      .products(
        {
          q: q || undefined,
          store: filters.store || undefined,
          sort: filters.sort,
          min_price: filters.min_price ? Number(filters.min_price) : undefined,
          max_price: filters.max_price ? Number(filters.max_price) : undefined,
          page,
          page_size: PAGE_SIZE,
          lang,
        },
        ctrl.signal,
      )
      .then((res) => {
        setItems(res.items);
        setTotal(res.total);
      })
      .catch((e) => {
        if (e.name !== "AbortError") {
          setItems([]);
          setTotal(0);
        }
      })
      .finally(() => setLoading(false));
    return () => ctrl.abort();
  }, [q, filters, page, lang]);

  return (
    <section className="max-w-6xl mx-auto px-5 py-12">
      <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-4 mb-8">
        <div>
          <h2 className="font-display text-3xl">
            {q ? `“${q}”` : tr(lang, "featured")}
          </h2>
          <p className="text-sm text-muted mt-1">
            {loading ? tr(lang, "loading") : `${total} ${tr(lang, "results")}`}
          </p>
        </div>
        <Filters value={filters} onChange={setFilters} />
      </div>

      {loading ? (
        <GridSkeleton count={PAGE_SIZE} />
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

      <Pagination page={page} pageSize={PAGE_SIZE} total={total} onPage={setPage} />
    </section>
  );
}
