export default function Loading() {
  return (
    <div className="flex items-center justify-center py-24" role="status" aria-label="페이지 로딩 중">
      <div className="flex flex-col items-center gap-3">
        <div className="w-8 h-8 border-3 border-[var(--color-primary-100)] border-t-[var(--color-primary)] rounded-full animate-spin" />
        <p className="text-sm text-[var(--color-text-muted)]">로딩 중...</p>
      </div>
    </div>
  );
}
