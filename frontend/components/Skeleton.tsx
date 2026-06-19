export function CardSkeleton() {
  return (
    <div className="border border-line bg-paper animate-pulse">
      <div className="aspect-[4/5] bg-paper-2" />
      <div className="p-3 space-y-2">
        <div className="h-3 bg-paper-2 w-full" />
        <div className="h-3 bg-paper-2 w-2/3" />
        <div className="h-6 bg-paper-2 w-1/2 mt-3" />
      </div>
    </div>
  );
}

export function GridSkeleton({ count = 10 }: { count?: number }) {
  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-4">
      {Array.from({ length: count }).map((_, i) => (
        <CardSkeleton key={i} />
      ))}
    </div>
  );
}
