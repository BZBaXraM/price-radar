"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import type { Store } from "@/lib/types";
import { tr } from "@/lib/i18n";
import { useAppStore } from "@/store/useAppStore";

export interface FilterState {
  store: string;
  sort: "relevance" | "price_asc" | "price_desc" | "offers";
  min_price: string;
  max_price: string;
}

export const DEFAULT_FILTERS: FilterState = {
  store: "",
  sort: "relevance",
  min_price: "",
  max_price: "",
};

export function Filters({
  value,
  onChange,
}: {
  value: FilterState;
  onChange: (next: FilterState) => void;
}) {
  const lang = useAppStore((s) => s.lang);
  const [stores, setStores] = useState<Store[]>([]);

  useEffect(() => {
    api.stores().then(setStores).catch(() => setStores([]));
  }, []);

  const set = (patch: Partial<FilterState>) => onChange({ ...value, ...patch });
  const selectCls =
    "bg-transparent border border-line px-3 py-2 text-sm outline-none focus:border-ink transition-colors";

  return (
    <div className="flex flex-col gap-2 sm:flex-row sm:flex-wrap sm:items-center sm:gap-3">
      <div className="grid grid-cols-2 gap-2 sm:contents">
        <select
          value={value.sort}
          onChange={(e) => set({ sort: e.target.value as FilterState["sort"] })}
          className={selectCls}
        >
          <option value="relevance">{tr(lang, "sort_relevance")}</option>
          <option value="price_asc">{tr(lang, "sort_price_asc")}</option>
          <option value="price_desc">{tr(lang, "sort_price_desc")}</option>
          <option value="offers">{tr(lang, "sort_offers")}</option>
        </select>

        <select
          value={value.store}
          onChange={(e) => set({ store: e.target.value })}
          className={selectCls}
        >
          <option value="">{tr(lang, "all_stores")}</option>
          {stores.map((s) => (
            <option key={s.slug} value={s.slug}>
              {s.name}
            </option>
          ))}
        </select>
      </div>

      <div className="grid grid-cols-2 gap-2 sm:contents">
        <input
          type="number"
          inputMode="numeric"
          value={value.min_price}
          onChange={(e) => set({ min_price: e.target.value })}
          placeholder={tr(lang, "price_from")}
          className={`${selectCls} sm:w-28`}
        />
        <input
          type="number"
          inputMode="numeric"
          value={value.max_price}
          onChange={(e) => set({ max_price: e.target.value })}
          placeholder={tr(lang, "price_to")}
          className={`${selectCls} sm:w-28`}
        />
      </div>

      <button
        onClick={() => onChange(DEFAULT_FILTERS)}
        className="text-sm text-muted hover:text-accent underline underline-offset-4 transition-colors self-start sm:self-auto"
      >
        {tr(lang, "reset")}
      </button>
    </div>
  );
}
