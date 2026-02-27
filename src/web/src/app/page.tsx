import Link from "next/link";
import { MediCheckLogo } from "@/components/common/MediCheckLogo";
import { AdBanner } from "@/components/ads/AdBanner";

export default function HomePage() {
  return (
    <>
      {/* Hero */}
      <section className="bg-gradient-to-b from-[var(--color-primary)] to-[var(--color-primary-dark)] text-white py-20">
        <div className="max-w-3xl mx-auto px-4 text-center">
          <MediCheckLogo size="lg" showText={false} className="justify-center mb-6 [&_path]:fill-white [&_rect]:fill-[var(--color-accent)]" />
          <h1 className="text-4xl font-bold mb-4 break-keep leading-tight">
            이 약이랑 이 영양제,
            <br />
            같이 먹어도 될까?
          </h1>
          <p className="text-lg text-blue-200 mb-8">
            3초 만에 확인하는 복약 안전 체커
          </p>
          <Link
            href="/check"
            className="inline-block px-8 py-3.5 rounded-xl text-[var(--color-primary)] font-semibold bg-white hover:bg-gray-100 shadow-lg hover:shadow-xl transition-all active:scale-[0.98]"
          >
            상호작용 확인하기
          </Link>
        </div>
      </section>

      {/* Trust badges */}
      <section className="py-10 border-b border-gray-100">
        <div className="max-w-3xl mx-auto px-4">
          <div className="grid grid-cols-3 gap-6 text-center">
            <div>
              <div className="w-12 h-12 mx-auto mb-2 rounded-full bg-[var(--color-primary-50)] flex items-center justify-center">
                <svg className="w-6 h-6 text-[var(--color-primary)]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                </svg>
              </div>
              <p className="text-sm font-semibold text-gray-900">식약처 공공데이터</p>
              <p className="text-xs text-gray-500 mt-0.5">공식 데이터 기반</p>
            </div>
            <div>
              <div className="w-12 h-12 mx-auto mb-2 rounded-full bg-[var(--color-primary-50)] flex items-center justify-center">
                <svg className="w-6 h-6 text-[var(--color-primary)]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
              <p className="text-sm font-semibold text-gray-900">3초 확인</p>
              <p className="text-xs text-gray-500 mt-0.5">빠른 상호작용 체크</p>
            </div>
            <div>
              <div className="w-12 h-12 mx-auto mb-2 rounded-full bg-[var(--color-primary-50)] flex items-center justify-center">
                <svg className="w-6 h-6 text-[var(--color-primary)]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <p className="text-sm font-semibold text-gray-900">완전 무료</p>
              <p className="text-xs text-gray-500 mt-0.5">회원가입 없이 이용</p>
            </div>
          </div>
        </div>
      </section>

      {/* 홈 광고 */}
      <AdBanner slot="home-mid" format="auto" className="max-w-3xl mx-auto px-4" />

      {/* Features */}
      <section className="py-16">
        <div className="max-w-3xl mx-auto px-4">
          <h2 className="text-2xl font-bold text-center text-gray-900 mb-10">
            MediCheck로 할 수 있는 것
          </h2>
          <div className="grid gap-6 sm:grid-cols-3">
            <Link href="/check" className="group block bg-white rounded-xl border border-gray-200 p-6 shadow-sm hover:shadow-md hover:border-[var(--color-primary-100)] transition-all">
              <div className="w-10 h-10 rounded-lg bg-blue-50 flex items-center justify-center mb-3 group-hover:bg-blue-100 transition-colors">
                <svg className="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
                </svg>
              </div>
              <h3 className="font-semibold text-gray-900 mb-1">상호작용 체크</h3>
              <p className="text-sm text-gray-500">복용 중인 약과 영양제의 상호작용을 확인하세요.</p>
            </Link>
            <Link href="/tips" className="group block bg-white rounded-xl border border-gray-200 p-6 shadow-sm hover:shadow-md hover:border-[var(--color-primary-100)] transition-all">
              <div className="w-10 h-10 rounded-lg bg-emerald-50 flex items-center justify-center mb-3 group-hover:bg-emerald-100 transition-colors">
                <svg className="w-5 h-5 text-emerald-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                </svg>
              </div>
              <h3 className="font-semibold text-gray-900 mb-1">건강팁</h3>
              <p className="text-sm text-gray-500">약과 영양제를 안전하게 복용하는 정보를 확인하세요.</p>
            </Link>
            <Link href="/cabinet" className="group block bg-white rounded-xl border border-gray-200 p-6 shadow-sm hover:shadow-md hover:border-[var(--color-primary-100)] transition-all">
              <div className="w-10 h-10 rounded-lg bg-amber-50 flex items-center justify-center mb-3 group-hover:bg-amber-100 transition-colors">
                <svg className="w-5 h-5 text-amber-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                </svg>
              </div>
              <h3 className="font-semibold text-gray-900 mb-1">내 복약함</h3>
              <p className="text-sm text-gray-500">복용 중인 약과 영양제를 관리하세요.</p>
            </Link>
          </div>
        </div>
      </section>
    </>
  );
}
