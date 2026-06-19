"use client";

import { use } from "react";
import { ProductDetailView } from "@/components/ProductDetail";

export default function ProductPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);
  return <div className="animate-page-enter"><ProductDetailView id={Number(id)} /></div>;
}
