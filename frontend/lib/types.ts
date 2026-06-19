export type Lang = "az" | "ru" | "en";

export interface ProductSummary {
  id: number;
  title: string;
  brand: string | null;
  model: string | null;
  category: string | null;
  category_label: string | null;
  image_url: string | null;
  best_price: number | null;
  best_store: string | null;
  currency: string;
  offers_count: number;
}

export interface Offer {
  id: number;
  store_slug: string;
  store_name: string;
  source_url: string;
  price: number;
  currency: string;
  in_stock: boolean;
  in_stock_label: string;
  image_url: string | null;
  scraped_at: string;
}

export interface ProductDetail extends ProductSummary {
  offers: Offer[];
}

export interface ProductListResponse {
  items: ProductSummary[];
  total: number;
  page: number;
  page_size: number;
}

export interface Store {
  id: number;
  slug: string;
  name: string;
  base_url: string;
  requires_browser: boolean;
  active: boolean;
  last_scraped_at: string | null;
  last_status: string | null;
}

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
}

export interface PriceUpdate {
  product_id: number;
  product_title: string;
  store_slug: string;
  old_price: number | null;
  new_price: number;
  in_stock: boolean;
  currency: string;
  observed_at: string;
}
