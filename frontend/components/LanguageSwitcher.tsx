"use client";

import { useAppStore } from "@/store/useAppStore";
import { LANGS } from "@/lib/i18n";

export function LanguageSwitcher() {
  const lang = useAppStore((s) => s.lang);
  const setLang = useAppStore((s) => s.setLang);

  return (
    <div className="flex items-center border border-line divide-x divide-line">
      {LANGS.map(({ code, label }) => (
        <button
          key={code}
          onClick={() => setLang(code)}
          className={`px-2.5 py-1 text-xs font-medium tracking-wide transition-colors ${
            lang === code
              ? "bg-ink text-paper"
              : "text-muted hover:text-ink"
          }`}
          aria-pressed={lang === code}
        >
          {label}
        </button>
      ))}
    </div>
  );
}
