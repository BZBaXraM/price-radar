"use client";

import { useEffect, useRef, useState } from "react";
import Link from "next/link";
import { WS_BASE } from "@/lib/api";
import type { PriceUpdate } from "@/lib/types";
import { formatPrice, STORE_NAMES, storeColor } from "@/lib/format";
import { tr } from "@/lib/i18n";
import { useAppStore } from "@/store/useAppStore";

interface Toast extends PriceUpdate {
  key: string;
}

export function LivePriceToaster() {
  const lang = useAppStore((s) => s.lang);
  const [toasts, setToasts] = useState<Toast[]>([]);
  const [exiting, setExiting] = useState<Set<string>>(new Set());
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    let closed = false;
    let retry: ReturnType<typeof setTimeout>;

    function connect() {
      if (closed) return;
      let ws: WebSocket;
      try {
        ws = new WebSocket(`${WS_BASE}/ws/prices`);
      } catch {
        retry = setTimeout(connect, 5000);
        return;
      }
      wsRef.current = ws;

      ws.onmessage = (ev) => {
        try {
          const data = JSON.parse(ev.data);
          if (data.type !== "price_updates" || !Array.isArray(data.changes)) return;
          // Only surface genuine price drops/changes (skip first-seen inserts).
          const real: PriceUpdate[] = data.changes.filter(
            (c: PriceUpdate) => c.old_price != null && c.old_price !== c.new_price,
          );
          if (real.length === 0) return;
          const fresh = real.slice(0, 3).map((c) => ({
            ...c,
            key: `${c.product_id}-${c.store_slug}-${Date.now()}-${Math.random()}`,
          }));
          setToasts((t) => [...fresh, ...t].slice(0, 4));
          fresh.forEach((f) => {
            setTimeout(() => {
              setExiting((prev) => { const s = new Set(prev); s.add(f.key); return s; });
              setTimeout(() => {
                setToasts((t) => t.filter((x) => x.key !== f.key));
                setExiting((prev) => { const s = new Set(prev); s.delete(f.key); return s; });
              }, 300);
            }, 7700);
          });
        } catch {
          /* ignore malformed */
        }
      };

      ws.onclose = () => {
        if (!closed) retry = setTimeout(connect, 5000);
      };
      ws.onerror = () => ws.close();
    }

    connect();
    return () => {
      closed = true;
      clearTimeout(retry);
      wsRef.current?.close();
    };
  }, []);

  if (toasts.length === 0) return null;

  return (
    <div className="fixed bottom-5 left-5 z-40 flex flex-col gap-2 w-[min(90vw,320px)]">
      {toasts.map((t) => {
        const drop = t.old_price != null && t.new_price < t.old_price;
        return (
          <Link
            key={t.key}
            href={`/product/${t.product_id}`}
            className={`bg-paper border border-ink p-3 block hover:bg-paper-2 transition-colors ${exiting.has(t.key) ? "animate-fade-out" : "animate-fade-up"}`}
          >
            <div className="flex items-center gap-2 mb-1">
              <span
                className="inline-block w-2 h-2 rounded-full"
                style={{ backgroundColor: storeColor(t.store_slug) }}
              />
              <span className="text-[11px] uppercase tracking-wide text-muted">
                {tr(lang, "live_update")} · {STORE_NAMES[t.store_slug] ?? t.store_slug}
              </span>
            </div>
            <p className="text-sm line-clamp-1">{t.product_title}</p>
            <p className="text-sm mt-1">
              {t.old_price != null && (
                <span className="text-muted line-through mr-2">
                  {formatPrice(t.old_price, t.currency)}
                </span>
              )}
              <span
                className="font-display text-base"
                style={{ color: drop ? "var(--color-deal)" : "var(--color-ink)" }}
              >
                {formatPrice(t.new_price, t.currency)}
              </span>
            </p>
          </Link>
        );
      })}
    </div>
  );
}
