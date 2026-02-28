"use client";

export default function OfflinePage() {
  return (
    <section className="max-w-xl mx-auto px-4 py-24 text-center">
      <div className="w-16 h-16 mx-auto mb-6 rounded-full bg-[var(--color-primary-50)] flex items-center justify-center">
        <svg className="w-8 h-8 text-[var(--color-text-muted)]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M18.364 5.636a9 9 0 010 12.728M5.636 18.364a9 9 0 010-12.728m2.828 9.9a5 5 0 010-7.072m7.072 0a5 5 0 010 7.072M13 12a1 1 0 11-2 0 1 1 0 012 0z" />
        </svg>
      </div>
      <h1 className="text-2xl font-bold text-[var(--color-text)] mb-3">인터넷 연결 없음</h1>
      <p className="text-[var(--color-text-secondary)] mb-8">
        네트워크에 연결되어 있지 않습니다.
        <br />
        연결을 확인하고 다시 시도해주세요.
      </p>
      <button
        onClick={() => window.location.reload()}
        className="px-6 py-3 rounded-xl font-semibold text-white bg-[var(--color-primary)] hover:bg-[var(--color-primary-dark)] shadow-md transition-all"
      >
        다시 시도
      </button>
    </section>
  );
}
