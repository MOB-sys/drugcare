import { SEVERITY_CONFIG, SEVERITY_ORDER, type Severity } from "@/lib/constants/severity";
import type { InteractionCheckResponse } from "@/types/interaction";

interface ResultSummaryCardProps {
  data: InteractionCheckResponse;
}

/** Count interactions per severity level. */
function countBySeverity(data: InteractionCheckResponse): Record<Severity, number> {
  const counts: Record<Severity, number> = { danger: 0, warning: 0, caution: 0, info: 0 };
  for (const r of data.results) {
    const sev = r.severity as Severity;
    if (sev in counts) counts[sev]++;
  }
  return counts;
}

/** Determine the worst severity present and return an action summary message. */
function getActionSummary(data: InteractionCheckResponse, counts: Record<Severity, number>): { message: string; className: string } | null {
  if (counts.danger > 0) {
    return {
      message: "위험한 상호작용이 발견되었습니다. 반드시 전문가와 상담하세요.",
      className: "text-red-700 bg-red-50 border-red-200 dark:text-red-300 dark:bg-red-950/40 dark:border-red-800",
    };
  }
  if (counts.warning > 0) {
    return {
      message: "주의가 필요한 조합이 있습니다. 아래 대처 방법을 확인하세요.",
      className: "text-amber-700 bg-amber-50 border-amber-200 dark:text-amber-300 dark:bg-amber-950/40 dark:border-amber-800",
    };
  }
  if (counts.caution > 0) {
    return {
      message: "경미한 주의사항이 있습니다. 아래 대처 방법을 참고하세요.",
      className: "text-blue-700 bg-blue-50 border-blue-200 dark:text-blue-300 dark:bg-blue-950/40 dark:border-blue-800",
    };
  }
  if (data.interactions_found === 0) {
    return {
      message: "확인된 상호작용이 없습니다. 안심하고 복용하세요.",
      className: "text-emerald-700 bg-emerald-50 border-emerald-200 dark:text-emerald-300 dark:bg-emerald-950/40 dark:border-emerald-800",
    };
  }
  return null;
}

export function ResultSummaryCard({ data }: ResultSummaryCardProps) {
  const isDanger = data.has_danger;
  const hasInteractions = data.interactions_found > 0;
  const counts = countBySeverity(data);
  const total = data.interactions_found || 1;
  const actionSummary = getActionSummary(data, counts);

  return (
    <div
      className={`rounded-xl border p-6 ${
        isDanger
          ? "border-red-200 bg-red-50/50 dark:border-red-800 dark:bg-red-950/30"
          : hasInteractions
            ? "border-orange-200 bg-orange-50/50 dark:border-orange-800 dark:bg-orange-950/30"
            : "border-emerald-200 bg-emerald-50/50 dark:border-emerald-800 dark:bg-emerald-950/30"
      }`}
    >
      <div className="flex items-center gap-3 mb-3">
        <div
          className={`w-12 h-12 rounded-full flex items-center justify-center shrink-0 ${
            isDanger
              ? "bg-red-100 animate-pulse-danger"
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
          <h2 className="text-lg font-bold text-gray-900 dark:text-gray-100">
            {isDanger
              ? "주의가 필요한 조합입니다"
              : hasInteractions
                ? "일부 상호작용이 발견되었습니다"
                : "특별한 상호작용이 없습니다"}
          </h2>
          <p className="text-sm text-gray-600 dark:text-gray-400">
            {data.total_checked}개 조합 확인 · {data.interactions_found}건 발견
          </p>
        </div>
      </div>

      {/* Severity Breakdown Bar */}
      {hasInteractions && (
        <div className="mt-4">
          <div className="flex h-2.5 w-full rounded-full overflow-hidden bg-gray-200">
            {SEVERITY_ORDER.map((sev) => {
              const count = counts[sev];
              if (count === 0) return null;
              const config = SEVERITY_CONFIG[sev];
              const widthPercent = (count / total) * 100;
              return (
                <div
                  key={sev}
                  className={`${config.barColor} transition-all`}
                  style={{ width: `${widthPercent}%` }}
                  title={`${config.label}(${config.labelEn}) ${count}건`}
                />
              );
            })}
          </div>
          <div className="flex flex-wrap gap-x-4 gap-y-1 mt-2">
            {SEVERITY_ORDER.map((sev) => {
              const count = counts[sev];
              if (count === 0) return null;
              const config = SEVERITY_CONFIG[sev];
              return (
                <span key={sev} className="inline-flex items-center gap-1.5 text-xs text-gray-600">
                  <span className={`w-2 h-2 rounded-full ${config.dotColor}`} />
                  {config.label} {count}건
                </span>
              );
            })}
          </div>
        </div>
      )}

      {/* Action summary line */}
      {actionSummary && (
        <div className={`mt-4 rounded-lg border p-3 flex items-start gap-2 ${actionSummary.className}`}>
          <svg
            className="w-4 h-4 mt-0.5 shrink-0"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
            aria-hidden="true"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
          <p className="text-sm font-medium">{actionSummary.message}</p>
        </div>
      )}
    </div>
  );
}
