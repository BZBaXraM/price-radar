import { STORE_NAMES, storeColor } from "@/lib/format";

export function StoreBadge({ slug, size = "sm" }: { slug: string; size?: "sm" | "md" }) {
  const name = STORE_NAMES[slug] ?? slug;
  return (
    <span
      className={`inline-flex items-center gap-1.5 font-medium ${
        size === "sm" ? "text-xs" : "text-sm"
      }`}
    >
      <span
        className="inline-block w-2 h-2 rounded-full"
        style={{ backgroundColor: storeColor(slug) }}
      />
      {name}
    </span>
  );
}
