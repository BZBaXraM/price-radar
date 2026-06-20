"use client";

import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { useState, useEffect } from "react";
import { useAppStore } from "@/store/useAppStore";
import { tr } from "@/lib/i18n";
import { LanguageSwitcher } from "./LanguageSwitcher";
import { ThemeToggle } from "./ThemeToggle";

export function Header() {
  const lang = useAppStore((s) => s.lang);
  const toggleChat = useAppStore((s) => s.toggleChat);
  const router = useRouter();
  const params = useSearchParams();
  const [q, setQ] = useState("");

  useEffect(() => {
    setQ(params.get("q") ?? "");
  }, [params]);

  function submit(e: React.FormEvent) {
    e.preventDefault();
    const sp = new URLSearchParams();
    if (q.trim()) sp.set("q", q.trim());
    router.push(`/?${sp.toString()}`);
  }

  return (
    <header className="sticky top-0 z-30 bg-paper/90 backdrop-blur border-b border-line">
      <div className="max-w-6xl mx-auto px-5 h-16 flex items-center gap-4">
        <Link href="/" className="shrink-0 group">
          <span className="font-display text-2xl tracking-tight">
            Price<span className="text-accent">Radar</span>
          </span>
        </Link>

        <form onSubmit={submit} className="flex-1 max-w-xl mx-auto hidden sm:block">
          <input
            value={q}
            onChange={(e) => setQ(e.target.value)}
            placeholder={tr(lang, "search_placeholder")}
            className="w-full bg-transparent border-b border-line focus:border-ink py-2 px-1 text-sm outline-none transition-colors placeholder:text-muted"
          />
        </form>

        <div className="flex items-center gap-2 sm:gap-3 shrink-0">
          <button
            onClick={toggleChat}
            className="hidden sm:block text-sm font-medium border-2 border-ink px-3 py-1.5 hover:-translate-y-px transition-transform"
          >
            {tr(lang, "ai_title")}
          </button>
          <ThemeToggle />
          <LanguageSwitcher />
        </div>
      </div>

      <form onSubmit={submit} className="sm:hidden max-w-6xl mx-auto px-5 pb-3">
        <input
          value={q}
          onChange={(e) => setQ(e.target.value)}
          placeholder={tr(lang, "search_placeholder")}
          className="w-full bg-transparent border-b border-line focus:border-ink py-2 px-1 text-sm outline-none placeholder:text-muted"
        />
      </form>
    </header>
  );
}
