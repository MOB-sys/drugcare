import { Skeleton } from "@/components/common/Skeleton";

export default function CheckResultLoading() {
  return (
    <div className="max-w-2xl mx-auto px-4 py-6">
      <Skeleton className="h-4 w-48 mb-4" />
      <Skeleton className="h-7 w-64 mb-6" />
      <div className="space-y-4">
        <Skeleton className="h-32 w-full rounded-xl" />
        <Skeleton className="h-24 w-full rounded-xl" />
        <Skeleton className="h-24 w-full rounded-xl" />
      </div>
    </div>
  );
}
