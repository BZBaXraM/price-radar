"use client";

import { useEffect } from "react";
import Link from "next/link";

export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error(error);
  }, [error]);

  return (
    <div className="max-w-6xl mx-auto px-5 py-32 text-center animate-page-enter">
      <p className="font-display text-4xl">Xəta baş verdi</p>
      <p className="text-muted mt-3 text-sm">
        Gözlənilməz xəta. Yenidən cəhd edin.
        {error.digest && (
          <span className="block mt-1 font-mono text-xs opacity-50">{error.digest}</span>
        )}
      </p>
      <div className="flex items-center justify-center gap-4 mt-8">
        <button
          onClick={reset}
          className="bg-ink text-paper text-sm px-4 py-2 hover:bg-accent transition-colors"
        >
          Yenidən cəhd et
        </button>
        <Link href="/" className="text-sm underline underline-offset-4 text-accent">
          Ana səhifəyə qayıt
        </Link>
      </div>
    </div>
  );
}
