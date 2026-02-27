/** 범용 스켈레톤 플레이스홀더. */

interface SkeletonProps {
  className?: string;
}

export function Skeleton({ className = "" }: SkeletonProps) {
  return (
    <div
      className={`animate-pulse rounded-lg bg-[var(--color-border)] ${className}`}
      aria-hidden="true"
    />
  );
}

/** 약물/영양제 상세 페이지용 스켈레톤. */
export function DetailPageSkeleton() {
  return (
    <div className="max-w-5xl mx-auto px-4 py-6">
      <Skeleton className="h-4 w-48 mb-4" />
      <div className="flex gap-6 mb-6">
        <Skeleton className="w-32 h-32 rounded-xl shrink-0" />
        <div className="flex-1 space-y-3">
          <Skeleton className="h-7 w-3/4" />
          <Skeleton className="h-4 w-1/2" />
          <Skeleton className="h-4 w-1/3" />
        </div>
      </div>
      <div className="space-y-4">
        <Skeleton className="h-24 w-full rounded-xl" />
        <Skeleton className="h-32 w-full rounded-xl" />
        <Skeleton className="h-20 w-full rounded-xl" />
      </div>
    </div>
  );
}

/** 검색 결과 리스트용 스켈레톤. */
export function SearchResultSkeleton() {
  return (
    <div className="space-y-2" aria-hidden="true">
      {[1, 2, 3, 4].map((i) => (
        <div key={i} className="flex items-center gap-3 p-3 rounded-xl">
          <Skeleton className="w-10 h-10 rounded-lg shrink-0" />
          <div className="flex-1 space-y-2">
            <Skeleton className="h-4 w-3/4" />
            <Skeleton className="h-3 w-1/2" />
          </div>
        </div>
      ))}
    </div>
  );
}
