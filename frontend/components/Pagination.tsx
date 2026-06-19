"use client";

import { tr } from "@/lib/i18n";
import { useAppStore } from "@/store/useAppStore";

export function Pagination({
  page,
  pageSize,
  total,
  onPage,
}: {
  page: number;
  pageSize: number;
  total: number;
  onPage: (p: number) => void;
}) {
  const lang = useAppStore((s) => s.lang);
  const pages = Math.max(1, Math.ceil(total / pageSize));
  if (pages <= 1) return null;

  const window: number[] = [];
  const start = Math.max(1, page - 2);
  const end = Math.min(pages, start + 4);
  for (let i = start; i <= end; i++) window.push(i);

  return (
    <div className="flex items-center justify-center gap-1 mt-12">
      <button
        onClick={() => onPage(page - 1)}
        disabled={page <= 1}
        className="px-3 py-1.5 text-sm border border-line disabled:opacity-30 hover:border-ink transition-colors"
      >
        {tr(lang, "prev")}
      </button>
      {window.map((p) => (
        <button
          key={p}
          onClick={() => onPage(p)}
          className={`px-3 py-1.5 text-sm border transition-colors ${
            p === page ? "bg-ink text-paper border-ink" : "border-line hover:border-ink"
          }`}
        >
          {p}
        </button>
      ))}
      <button
        onClick={() => onPage(page + 1)}
        disabled={page >= pages}
        className="px-3 py-1.5 text-sm border border-line disabled:opacity-30 hover:border-ink transition-colors"
      >
        {tr(lang, "next")}
      </button>
    </div>
  );
}
