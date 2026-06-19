"use client";

import { useAppStore } from "@/store/useAppStore";
import { tr } from "@/lib/i18n";
import { STORE_NAMES, storeColor } from "@/lib/format";

export function Hero() {
  const lang = useAppStore((s) => s.lang);

  return (
    <section className="border-b border-line">
      <div className="max-w-6xl mx-auto px-5 py-16 sm:py-24 grid grid-cols-1 lg:grid-cols-12 gap-8 items-end">
        <div className="lg:col-span-8">
          <p className="text-accent text-sm font-medium tracking-wide uppercase mb-4">
            {tr(lang, "tagline")}
          </p>
          <h1 className="font-display text-4xl sm:text-6xl lg:text-7xl leading-[1.02]">
            {tr(lang, "hero_title")}
          </h1>
          <p className="mt-6 max-w-prose text-muted leading-relaxed">
            {tr(lang, "hero_sub")}
          </p>
        </div>
        <div className="lg:col-span-4 flex flex-col gap-2 lg:items-end">
          {Object.entries(STORE_NAMES).map(([slug, name]) => (
            <div key={slug} className="flex items-center gap-2 text-sm">
              <span
                className="inline-block w-2.5 h-2.5 rounded-full"
                style={{ backgroundColor: storeColor(slug) }}
              />
              <span className="text-muted">{name}</span>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
