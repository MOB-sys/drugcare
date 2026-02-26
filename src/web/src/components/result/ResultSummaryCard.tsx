import type { InteractionCheckResponse } from "@/types/interaction";

interface ResultSummaryCardProps {
  data: InteractionCheckResponse;
}

export function ResultSummaryCard({ data }: ResultSummaryCardProps) {
  const isDanger = data.has_danger;
  const hasInteractions = data.interactions_found > 0;

  return (
    <div
      className={`rounded-xl border p-6 ${
        isDanger
          ? "border-red-200 bg-red-50/50"
          : hasInteractions
            ? "border-orange-200 bg-orange-50/50"
            : "border-emerald-200 bg-emerald-50/50"
      }`}
    >
      <div className="flex items-center gap-3 mb-3">
        <div
          className={`w-12 h-12 rounded-full flex items-center justify-center shrink-0 ${
            isDanger
              ? "bg-red-100"
              : hasInteractions
                ? "bg-orange-100"
                : "bg-emerald-100"
          }`}
        >
          {isDanger ? (
            <svg className="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z" />
            </svg>
          ) : hasInteractions ? (
            <svg className="w-6 h-6 text-orange-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          ) : (
            <svg className="w-6 h-6 text-emerald-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
            </svg>
          )}
        </div>
        <div>
          <h2 className="text-lg font-bold text-gray-900">
            {isDanger
              ? "주의가 필요한 조합입니다"
              : hasInteractions
                ? "일부 상호작용이 발견되었습니다"
                : "특별한 상호작용이 없습니다"}
          </h2>
          <p className="text-sm text-gray-600">
            {data.total_checked}개 조합 확인 · {data.interactions_found}건 발견
          </p>
        </div>
      </div>
    </div>
  );
}
