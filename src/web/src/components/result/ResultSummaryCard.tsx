import type { InteractionCheckResponse } from "@/types/interaction";

interface ResultSummaryCardProps {
  data: InteractionCheckResponse;
}

export function ResultSummaryCard({ data }: ResultSummaryCardProps) {
  return (
    <div
      className={`rounded-lg border p-6 ${
        data.has_danger
          ? "border-red-300 bg-red-50"
          : data.interactions_found > 0
            ? "border-orange-300 bg-orange-50"
            : "border-green-300 bg-green-50"
      }`}
    >
      <div className="flex items-center gap-3 mb-3">
        <span className="text-3xl">
          {data.has_danger ? "⚠️" : data.interactions_found > 0 ? "💊" : "✅"}
        </span>
        <div>
          <h2 className="text-lg font-bold text-gray-900">
            {data.has_danger
              ? "주의가 필요한 조합입니다"
              : data.interactions_found > 0
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
