import Link from "next/link";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Səhifə tapılmadı",
};

export default function NotFound() {
  return (
    <div className="max-w-6xl mx-auto px-5 py-32 text-center animate-page-enter">
      <p className="font-display text-8xl text-line select-none">404</p>
      <p className="font-display text-3xl mt-4">Səhifə tapılmadı</p>
      <p className="text-muted mt-3 text-sm">
        Axtardığınız səhifə mövcud deyil və ya köçürülüb.
      </p>
      <Link
        href="/"
        className="inline-block mt-8 bg-ink text-paper text-sm px-4 py-2 hover:bg-accent transition-colors"
      >
        Ana səhifəyə qayıt
      </Link>
    </div>
  );
}
