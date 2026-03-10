import Link from "next/link";

export default function NotFound() {
  return (
    <section className="max-w-xl mx-auto px-4 py-24 text-center">
      <div className="w-16 h-16 mx-auto mb-6 rounded-full bg-[var(--color-primary-50)] flex items-center justify-center">
        <svg className="w-8 h-8 text-[var(--color-primary)]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
        </svg>
      </div>
      <div className="text-6xl font-bold text-[var(--color-primary)] mb-4">404</div>
      <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-3">
        페이지를 찾을 수 없습니다
      </h1>
      <p className="text-gray-500 dark:text-gray-400 mb-8">
        요청하신 페이지가 존재하지 않거나, 주소가 변경되었을 수 있습니다.
      </p>
      <div className="flex justify-center gap-4">
        <Link
          href="/"
          className="px-6 py-3 rounded-xl font-semibold text-white bg-[var(--color-primary)] hover:bg-[var(--color-primary-dark)] shadow-md transition-all"
        >
          홈으로 가기
        </Link>
        <Link
          href="/check"
          className="px-6 py-3 rounded-xl font-semibold border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
        >
          상호작용 체크
        </Link>
      </div>
    </section>
  );
}
