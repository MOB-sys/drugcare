/** 심각도별 UI 설정. */

export const SEVERITY_CONFIG = {
  danger: {
    label: "위험",
    className: "bg-red-100 text-red-800 border-red-300",
    cardClassName: "border-red-300 bg-red-50",
    iconColor: "text-red-600",
  },
  warning: {
    label: "경고",
    className: "bg-orange-100 text-orange-800 border-orange-300",
    cardClassName: "border-orange-300 bg-orange-50",
    iconColor: "text-orange-600",
  },
  caution: {
    label: "주의",
    className: "bg-yellow-100 text-yellow-800 border-yellow-300",
    cardClassName: "border-yellow-300 bg-yellow-50",
    iconColor: "text-yellow-600",
  },
  info: {
    label: "참고",
    className: "bg-blue-100 text-blue-800 border-blue-300",
    cardClassName: "border-blue-300 bg-blue-50",
    iconColor: "text-blue-600",
  },
} as const;

export type Severity = keyof typeof SEVERITY_CONFIG;

export const MIN_INTERACTION_ITEMS = 2;
export const MAX_INTERACTION_ITEMS = 20;
