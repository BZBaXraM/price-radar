"use client";

import { use } from "react";
import { ProductDetailView } from "@/components/ProductDetail";

export default function ProductPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);
  return <ProductDetailView id={Number(id)} />;
}
