import { SEVERITY_CONFIG, type Severity } from "@/lib/constants/severity";

interface SeverityBadgeProps {
  severity: Severity;
}

export function SeverityBadge({ severity }: SeverityBadgeProps) {
  const config = SEVERITY_CONFIG[severity];
  const isDanger = severity === "danger";

  return (
    <span
      className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold border ${config.className} ${isDanger ? "animate-pulse-danger" : ""}`}
    >
      <span className={`w-1.5 h-1.5 rounded-full ${config.dotColor}`} aria-hidden="true" />
      {config.label}
      <span className="hidden sm:inline text-[10px] font-medium opacity-70">({config.labelEn})</span>
    </span>
  );
}
