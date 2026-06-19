import { Suspense } from "react";
import { Hero } from "@/components/Hero";
import { Catalog } from "@/components/Catalog";
import { GridSkeleton } from "@/components/Skeleton";

export default function Home() {
  return (
    <div className="animate-page-enter">
      <Hero />
      <Suspense
        fallback={
          <div className="max-w-6xl mx-auto px-5 py-12">
            <GridSkeleton />
          </div>
        }
      >
        <Catalog />
      </Suspense>
    </div>
  );
}
