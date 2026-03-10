import type { Severity } from "@/lib/constants/severity";

interface ActionGuidanceBoxProps {
  severity: Severity;
}

const GUIDANCE_MAP: Record<Severity, string[]> = {
  danger: [
    "즉시 복용을 중단하고 의사 또는 약사와 상담하세요.",
    "두 약물을 동시에 복용하지 마세요.",
    "대체 약물에 대해 전문가와 상의하세요.",
  ],
  warning: [
    "복용 간격을 최소 2시간 이상 두세요.",
    "증상 변화를 주의 깊게 관찰하세요.",
    "다음 병원 방문 시 의사에게 알려주세요.",
  ],
  caution: [
    "일반적으로 함께 복용 가능하나, 이상 증상 시 전문가와 상담하세요.",
  ],
  info: [
    "현재까지 알려진 상호작용이 없습니다. 안심하고 복용하세요.",
  ],
};

const STYLE_MAP: Record<Severity, { container: string; icon: string }> = {
  danger: {
    container: "bg-red-50 border-red-200 text-red-700 dark:bg-red-950/40 dark:border-red-800 dark:text-red-300",
    icon: "text-red-500 dark:text-red-400",
  },
  warning: {
    container: "bg-amber-50 border-amber-200 text-amber-700 dark:bg-amber-950/40 dark:border-amber-800 dark:text-amber-300",
    icon: "text-amber-500 dark:text-amber-400",
  },
  caution: {
    container: "bg-blue-50 border-blue-200 text-blue-700 dark:bg-blue-950/40 dark:border-blue-800 dark:text-blue-300",
    icon: "text-blue-500 dark:text-blue-400",
  },
  info: {
    container: "bg-green-50 border-green-200 text-green-700 dark:bg-green-950/40 dark:border-green-800 dark:text-green-300",
    icon: "text-green-500 dark:text-green-400",
  },
};

/** Severity-based action guidance tip box. */
export function ActionGuidanceBox({ severity }: ActionGuidanceBoxProps) {
  const guidance = GUIDANCE_MAP[severity];
  const styles = STYLE_MAP[severity];

  return (
    <div className={`mt-1 rounded-lg border p-3 ${styles.container}`}>
      <div className="flex items-start gap-2">
        <svg
          className={`w-4 h-4 mt-0.5 shrink-0 ${styles.icon}`}
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
          aria-hidden="true"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"
          />
        </svg>
        <div className="flex-1 min-w-0">
          <p className="font-semibold text-xs mb-1">대처 방법</p>
          <ul className="space-y-0.5">
            {guidance.map((text) => (
              <li key={text} className="text-xs flex items-start gap-1.5">
                <span className="shrink-0 mt-1.5 w-1 h-1 rounded-full bg-current opacity-50" />
                <span>{text}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
}
