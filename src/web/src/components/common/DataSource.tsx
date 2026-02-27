/** 데이터 출처 + 수집일 표시 컴포넌트. */

interface DataSourceProps {
  /** "의약품안전나라" | "건강기능식품 정보" 등 */
  source?: string;
  /** 업데이트 날짜 문자열 (예: "2026.02.27") */
  updatedAt?: string;
  className?: string;
}

export function DataSource({
  source = "식약처 의약품안전나라",
  updatedAt,
  className = "",
}: DataSourceProps) {
  const dateStr = updatedAt || new Date().toLocaleDateString("ko-KR", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
  }).replace(/\. /g, ".").replace(/\.$/, "");

  return (
    <div className={`flex items-center gap-1.5 text-xs text-gray-400 ${className}`.trim()}>
      <svg className="w-3.5 h-3.5 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
      </svg>
      <span>{source} 기준</span>
      <span className="text-gray-300">·</span>
      <span>{dateStr} 업데이트</span>
    </div>
  );
}
