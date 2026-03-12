/**
 * 폴백 정보 섹션 — InfoSection과 유사하지만
 * "일반 정보" 배지 + 연한 배경으로 API 데이터와 시각적으로 구분.
 */

interface FallbackInfoSectionProps {
  title: string;
  content: string;
  id?: string;
}

export function FallbackInfoSection({
  title,
  content,
  id,
}: FallbackInfoSectionProps) {
  return (
    <section
      id={id}
      className="py-4 border-b border-gray-100 dark:border-gray-700 last:border-b-0 scroll-mt-24"
    >
      <div className="flex items-center gap-2 mb-2">
        <h2 className="text-lg font-semibold text-[var(--color-primary)]">
          {title}
        </h2>
        <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-amber-100 dark:bg-amber-900/40 text-amber-700 dark:text-amber-300">
          일반 정보
        </span>
      </div>
      <div className="rounded-lg bg-amber-50/50 dark:bg-amber-900/10 border border-amber-200/50 dark:border-amber-800/30 p-4">
        <p className="text-gray-700 dark:text-gray-300 leading-relaxed whitespace-pre-line break-keep text-sm">
          {content}
        </p>
        <p className="text-xs text-gray-400 dark:text-gray-500 mt-3">
          이 정보는 성분 및 약물 분류를 기반으로 작성된 일반적인 안내이며,
          개별 의약품의 허가 정보와 다를 수 있습니다. 정확한 정보는 의사·약사와
          상담하세요.
        </p>
      </div>
    </section>
  );
}
