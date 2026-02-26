import Link from "next/link";

export function EmptyState() {
  return (
    <div className="text-center py-16">
      <div className="text-5xl mb-4">💊</div>
      <h2 className="text-lg font-semibold text-gray-700 mb-2">
        복약함이 비어 있습니다
      </h2>
      <p className="text-sm text-gray-500 mb-6">
        약물이나 영양제를 검색해서 추가해보세요.
      </p>
      <Link
        href="/check"
        className="inline-block px-6 py-2.5 rounded-lg text-white font-medium bg-[var(--color-brand)] hover:bg-[var(--color-brand-dark)] transition-colors"
      >
        약물/영양제 검색하기
      </Link>
    </div>
  );
}
