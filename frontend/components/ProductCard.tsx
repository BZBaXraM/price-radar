"use client";

import Link from "next/link";
import type { ProductSummary } from "@/lib/types";
import { formatPrice } from "@/lib/format";
import { tr } from "@/lib/i18n";
import { useAppStore } from "@/store/useAppStore";
import { ProductImage } from "./ProductImage";
import { StoreBadge } from "./StoreBadge";

export function ProductCard({ p }: { p: ProductSummary }) {
  const lang = useAppStore((s) => s.lang);

  return (
    <Link
      href={`/product/${p.id}`}
      className="group flex flex-col border border-line bg-paper hover:border-ink transition-colors duration-200"
    >
      <div className="relative aspect-[4/5] overflow-hidden bg-paper-2">
        <ProductImage src={p.image_url} alt={p.title} className="w-full h-full p-4" />
        {p.offers_count > 1 && (
          <span className="absolute top-0 left-0 bg-ink text-paper text-[11px] font-medium px-2 py-1">
            {p.offers_count} {tr(lang, "offers")}
          </span>
        )}
        {p.brand && (
          <span className="absolute top-0 right-0 bg-paper/80 text-muted text-[11px] px-2 py-1 uppercase tracking-wide">
            {p.brand}
          </span>
        )}
      </div>

      <div className="flex flex-col gap-2 p-3 flex-1">
        {p.category_label && (
          <p className="text-[10px] text-muted uppercase tracking-wider">{p.category_label}</p>
        )}
        <h3 className="text-sm leading-snug line-clamp-2 min-h-[2.5rem]">{p.title}</h3>
        <div className="mt-auto pt-2 border-t border-line">
          <p className="text-[11px] text-muted uppercase tracking-wide">
            {tr(lang, "best_price")}
          </p>
          <div className="flex items-baseline justify-between gap-2">
            <span className="font-display text-xl text-ink">
              {formatPrice(p.best_price, p.currency)}
            </span>
            {p.best_store && <StoreBadge slug={p.best_store} />}
          </div>
        </div>
      </div>
    </Link>
  );
}
