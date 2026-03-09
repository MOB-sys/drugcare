import { SEVERITY_CONFIG, SEVERITY_ORDER } from "@/lib/constants/severity";

const SEVERITY_DESCRIPTIONS: Record<string, string> = {
  danger: "병용 금기 또는 심각한 부작용 가능",
  warning: "주의 필요, 의사/약사 상담 권장",
  caution: "경미한 영향 가능, 모니터링 필요",
  info: "참고 정보, 일반적으로 안전",
};

/** Horizontal legend explaining all severity levels with colors. */
export function SeverityLegend() {
  return (
    <div className="flex flex-wrap gap-x-5 gap-y-2 px-4 py-3 bg-gray-50 rounded-lg border border-gray-200 text-xs">
      {SEVERITY_ORDER.map((sev) => {
        const config = SEVERITY_CONFIG[sev];
        return (
          <div key={sev} className="flex items-center gap-1.5">
            <span className={`w-2.5 h-2.5 rounded-full ${config.dotColor} shrink-0`} />
            <span className="font-semibold text-gray-700">
              {config.label}
              <span className="font-normal text-gray-400 ml-0.5">({config.labelEn})</span>
            </span>
            <span className="text-gray-500 hidden sm:inline">— {SEVERITY_DESCRIPTIONS[sev]}</span>
          </div>
        );
      })}
    </div>
  );
}
