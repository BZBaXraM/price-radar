"use client";

import { useState } from "react";
import { placeholderFor } from "@/lib/format";

export function ProductImage({
  src,
  alt,
  className = "",
}: {
  src: string | null;
  alt: string;
  className?: string;
}) {
  const [failed, setFailed] = useState(false);

  if (!src || failed) {
    return (
      <div
        className={`flex items-center justify-center bg-paper-2 text-muted ${className}`}
        aria-label={alt}
      >
        <span className="font-display text-4xl opacity-40">{placeholderFor(alt)}</span>
      </div>
    );
  }

  return (
    // eslint-disable-next-line @next/next/no-img-element
    <img
      src={src}
      alt={alt}
      loading="lazy"
      onError={() => setFailed(true)}
      className={`img-editorial object-contain ${className}`}
    />
  );
}
