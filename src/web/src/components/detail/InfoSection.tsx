/** 상세 페이지 정보 블록 — 제목+본문 재사용 컴포넌트. */

interface InfoSectionProps {
  title: string;
  content: string | null;
  id?: string;
}

export function InfoSection({ title, content, id }: InfoSectionProps) {
  if (!content) return null;

  return (
    <section id={id} className="py-4 border-b border-gray-100 dark:border-gray-700 last:border-b-0 scroll-mt-24">
      <h2 className="text-lg font-semibold text-[var(--color-primary)] mb-2">{title}</h2>
      <p className="text-gray-700 dark:text-gray-300 leading-relaxed whitespace-pre-line break-keep">{content}</p>
    </section>
  );
}
