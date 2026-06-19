"use client";

import { useEffect } from "react";
import { useAppStore } from "@/store/useAppStore";
import { tr } from "@/lib/i18n";

export function ThemeToggle() {
  const theme = useAppStore((s) => s.theme);
  const toggleTheme = useAppStore((s) => s.toggleTheme);
  const lang = useAppStore((s) => s.lang);

  // Keep the <html> class in sync with the persisted theme (covers hydration
  // and changes from any tab).
  useEffect(() => {
    const root = document.documentElement;
    root.classList.toggle("dark", theme === "dark");
  }, [theme]);

  const isDark = theme === "dark";

  return (
    <button
      onClick={toggleTheme}
      aria-label={tr(lang, "theme_toggle")}
      title={tr(lang, isDark ? "theme_light" : "theme_dark")}
      className="w-8 h-8 flex items-center justify-center border border-line hover:border-ink transition-colors text-base"
    >
      {isDark ? "☀" : "☾"}
    </button>
  );
}
