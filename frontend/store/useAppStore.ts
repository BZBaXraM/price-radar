"use client";

import { create } from "zustand";
import { persist } from "zustand/middleware";
import type { Lang } from "@/lib/types";

export type Theme = "light" | "dark";

interface AppState {
  lang: Lang;
  setLang: (lang: Lang) => void;
  theme: Theme;
  setTheme: (theme: Theme) => void;
  toggleTheme: () => void;
  chatOpen: boolean;
  setChatOpen: (open: boolean) => void;
  toggleChat: () => void;
}

export const useAppStore = create<AppState>()(
  persist(
    (set) => ({
      lang: "az",
      setLang: (lang) => set({ lang }),
      theme: "light",
      setTheme: (theme) => set({ theme }),
      toggleTheme: () => set((s) => ({ theme: s.theme === "dark" ? "light" : "dark" })),
      chatOpen: false,
      setChatOpen: (chatOpen) => set({ chatOpen }),
      toggleChat: () => set((s) => ({ chatOpen: !s.chatOpen })),
    }),
    { name: "priceradar", partialize: (s) => ({ lang: s.lang, theme: s.theme }) },
  ),
);
