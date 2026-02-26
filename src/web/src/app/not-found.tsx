import Link from "next/link";

export default function NotFound() {
  return (
    <section className="max-w-xl mx-auto px-4 py-24 text-center">
      <div className="text-6xl font-bold text-[var(--color-brand)] mb-4">404</div>
      <h1 className="text-2xl font-bold text-gray-900 mb-3">
        페이지를 찾을 수 없습니다
      </h1>
      <p className="text-gray-500 mb-8">
        요청하신 페이지가 존재하지 않거나, 주소가 변경되었을 수 있습니다.
      </p>
      <div className="flex justify-center gap-4">
        <Link
          href="/"
          className="px-6 py-3 rounded-lg font-semibold text-white bg-[var(--color-brand)] hover:bg-[var(--color-brand-dark)] transition-colors"
        >
          홈으로 가기
        </Link>
        <Link
          href="/check"
          className="px-6 py-3 rounded-lg font-semibold border border-gray-300 text-gray-700 hover:bg-gray-50 transition-colors"
        >
          상호작용 체크
        </Link>
      </div>
    </section>
  );
}
