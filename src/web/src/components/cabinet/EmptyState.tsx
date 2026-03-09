import Link from "next/link";
export function EmptyState() {

  return (
    <div className="text-center py-16">
      <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-[var(--color-primary-50)] flex items-center justify-center">
        <svg className="w-8 h-8 text-[var(--color-primary)]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" />
        </svg>
      </div>
      <h2 className="text-lg font-semibold text-gray-700 mb-2">
        복약함이 비어 있습니다
      </h2>
      <p className="text-sm text-gray-500 mb-6">
        약물이나 영양제를 검색해서 추가해보세요.
      </p>
      <Link
        href="/check"
        className="inline-block px-6 py-2.5 rounded-xl text-white font-medium bg-[var(--color-primary)] hover:bg-[var(--color-primary-dark)] shadow-md transition-all"
      >
        약물/영양제 검색하기
      </Link>

      {/* 앱 출시 예정 안내 */}
      <div className="mt-8 pt-6 border-t border-gray-100">
        <p className="text-xs text-gray-400">
          앱 출시 예정 — 복약 리마인더 기능을 준비 중입니다
        </p>
      </div>
    </div>
  );
}
