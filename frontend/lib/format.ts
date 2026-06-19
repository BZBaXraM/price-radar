export function formatPrice(value: number | null | undefined, currency = "AZN"): string {
  if (value === null || value === undefined) return "—";
  const symbol = currency === "AZN" ? "₼" : currency;
  return `${value.toLocaleString("az-AZ", { minimumFractionDigits: 2, maximumFractionDigits: 2 })} ${symbol}`;
}

export const STORE_COLORS: Record<string, string> = {
  kontakt: "#c2410c",
  irshad: "#1a3a2e",
  wt: "#1e3a5f",
  bakuelectronics: "#7a1f2b",
};

export const STORE_NAMES: Record<string, string> = {
  kontakt: "KontaktHome",
  irshad: "İrşad",
  wt: "World Telecom",
  bakuelectronics: "Baku Electronics",
};

export function storeColor(slug: string): string {
  return STORE_COLORS[slug] ?? "#0a0a0a";
}

export function placeholderFor(title: string): string {
  return title.slice(0, 2).toUpperCase();
}
