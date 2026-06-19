import type {
  Lang,
  ProductDetail,
  ProductListResponse,
  Store,
} from "./types";

const API = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";
export const WS_BASE = process.env.NEXT_PUBLIC_WS_URL || "ws://127.0.0.1:8000";

export interface ProductQuery {
  q?: string;
  category?: string;
  brand?: string;
  store?: string;
  min_price?: number;
  max_price?: number;
  sort?: "relevance" | "price_asc" | "price_desc" | "offers";
  page?: number;
  page_size?: number;
  lang?: Lang;
}

function qs(params: Record<string, unknown> | ProductQuery): string {
  const sp = new URLSearchParams();
  for (const [k, v] of Object.entries(params as Record<string, unknown>)) {
    if (v !== undefined && v !== null && v !== "") sp.set(k, String(v));
  }
  const s = sp.toString();
  return s ? `?${s}` : "";
}

async function getJSON<T>(path: string, signal?: AbortSignal, lang?: Lang): Promise<T> {
  const headers: Record<string, string> = {};
  if (lang) headers["Accept-Language"] = lang;
  const res = await fetch(`${API}${path}`, { signal, headers });
  if (!res.ok) throw new Error(`API ${res.status}: ${path}`);
  return res.json() as Promise<T>;
}

export const api = {
  products(query: ProductQuery = {}, signal?: AbortSignal) {
    return getJSON<ProductListResponse>(`/api/products${qs(query)}`, signal, query.lang);
  },
  product(id: number, lang: Lang, signal?: AbortSignal) {
    return getJSON<ProductDetail>(`/api/products/${id}${qs({ lang })}`, signal, lang);
  },
  stores(signal?: AbortSignal) {
    return getJSON<Store[]>(`/api/stores`, signal);
  },
  async chat(message: string, lang: Lang, history: { role: string; content: string }[]) {
    const res = await fetch(`${API}/api/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json", "Accept-Language": lang },
      body: JSON.stringify({ message, lang, history }),
    });
    if (!res.ok) throw new Error(`chat ${res.status}`);
    return res.json() as Promise<{ reply: string; lang: Lang }>;
  },
};

export function apiBase() {
  return API;
}
