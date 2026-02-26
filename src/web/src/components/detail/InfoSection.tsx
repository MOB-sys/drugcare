/** 상세 페이지 정보 블록 — 제목+본문 재사용 컴포넌트. */

interface InfoSectionProps {
  title: string;
  content: string | null;
}

export function InfoSection({ title, content }: InfoSectionProps) {
  if (!content) return null;

  return (
    <section className="py-4 border-b border-gray-100 last:border-b-0">
      <h2 className="text-lg font-semibold text-[var(--color-primary)] mb-2">{title}</h2>
      <p className="text-gray-700 leading-relaxed whitespace-pre-line break-keep">{content}</p>
    </section>
  );
}
