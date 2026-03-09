/** 심각도별 UI 설정. */

export const SEVERITY_CONFIG = {
  danger: {
    label: "위험",
    labelEn: "Major",
    className: "bg-red-50 text-red-700 border-red-200",
    cardClassName: "border-red-200 bg-red-50/50",
    iconColor: "text-red-600",
    dotColor: "bg-red-500",
    borderColor: "border-l-red-500",
    barColor: "bg-red-500",
  },
  warning: {
    label: "경고",
    labelEn: "Moderate",
    className: "bg-orange-50 text-orange-700 border-orange-200",
    cardClassName: "border-orange-200 bg-orange-50/50",
    iconColor: "text-orange-600",
    dotColor: "bg-orange-500",
    borderColor: "border-l-orange-500",
    barColor: "bg-orange-500",
  },
  caution: {
    label: "주의",
    labelEn: "Minor",
    className: "bg-amber-50 text-amber-700 border-amber-200",
    cardClassName: "border-amber-200 bg-amber-50/50",
    iconColor: "text-amber-600",
    dotColor: "bg-amber-500",
    borderColor: "border-l-amber-500",
    barColor: "bg-amber-500",
  },
  info: {
    label: "참고",
    labelEn: "Info",
    className: "bg-blue-50 text-blue-700 border-blue-200",
    cardClassName: "border-blue-200 bg-blue-50/50",
    iconColor: "text-blue-600",
    dotColor: "bg-blue-500",
    borderColor: "border-l-blue-500",
    barColor: "bg-blue-500",
  },
} as const;

export type Severity = keyof typeof SEVERITY_CONFIG;

export const SEVERITY_ORDER: Severity[] = ["danger", "warning", "caution", "info"];

export const MIN_INTERACTION_ITEMS = 2;
export const MAX_INTERACTION_ITEMS = 20;
