import Link from "next/link";
import { PillRightLogo } from "@/components/common/PillRightLogo";
import { AdBanner } from "@/components/ads/AdBanner";
import { searchDrugs } from "@/lib/api/drugs";
import { searchSupplements } from "@/lib/api/supplements";

export const revalidate = 86400; // ISR: 24시간마다 재생성

import { SITE_URL } from "@/lib/constants/site";

const POPULAR_COMBOS = [
  { items: ["타이레놀", "오메가3"], label: "타이레놀 + 오메가3" },
  { items: ["아스피린", "오메가3"], label: "아스피린 + 오메가3" },
  { items: ["비타민D", "칼슘"], label: "비타민D + 칼슘" },
  { items: ["철분", "칼슘"], label: "철분 + 칼슘" },
  { items: ["유산균", "항생제"], label: "유산균 + 항생제" },
  { items: ["마그네슘", "비타민D"], label: "마그네슘 + 비타민D" },
  { items: ["아스피린", "이부프로펜"], label: "아스피린 + 이부프로펜" },
  { items: ["밀크씨슬", "비타민C"], label: "밀크씨슬 + 비타민C" },
];

/** 키워드로 약물/영양제를 검색하여 첫 번째 결과의 type:id:name을 반환 */
async function resolveKeyword(keyword: string): Promise<string | null> {
  try {
    const [drugRes, suppRes] = await Promise.all([
      searchDrugs(keyword, 1, 1).catch(() => ({ items: [] })),
      searchSupplements(keyword, 1, 1).catch(() => ({ items: [] })),
    ]);
    const drug = drugRes.items[0];
    const supp = suppRes.items[0];
    if (drug) return `drug:${drug.id}:${encodeURIComponent(drug.item_name)}`;
    if (supp) return `supplement:${supp.id}:${encodeURIComponent(supp.product_name)}`;
    return null;
  } catch {
    return null;
  }
}

/** 인기 조합의 결과 URL을 미리 빌드. 두 키워드 모두 DB에 있는 조합만 반환. */
async function resolveComboUrls(): Promise<Map<string, string>> {
  const urlMap = new Map<string, string>();
  const results = await Promise.all(
    POPULAR_COMBOS.map(async (combo) => {
      const resolved = await Promise.all(combo.items.map(resolveKeyword));
      const valid = resolved.filter(Boolean) as string[];
      if (valid.length >= 2) {
        return { label: combo.label, url: `/check/result?items=${valid.join(",")}` };
      }
      return null; // DB에 없는 조합은 제외
    }),
  );
  for (const r of results) {
    if (r) urlMap.set(r.label, r.url);
  }
  return urlMap;
}

const websiteJsonLd = {
  "@context": "https://schema.org",
  "@type": "WebSite",
  name: "약잘알",
  url: SITE_URL,
  potentialAction: {
    "@type": "SearchAction",
    target: {
      "@type": "EntryPoint",
      urlTemplate: `${SITE_URL}/check?q={search_term_string}`,
    },
    "query-input": "required name=search_term_string",
  },
};

export default async function HomePage() {
  const comboUrls = await resolveComboUrls();

  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(websiteJsonLd).replace(/</g, '\\u003c') }}
      />

      {/* Hero */}
      <section className="bg-gradient-to-b from-[var(--color-primary)] to-[var(--color-primary-dark)] text-white py-20">
        <div className="max-w-3xl mx-auto px-4 text-center">
          <PillRightLogo size="lg" showText={false} className="justify-center mb-6 [&_path]:fill-white [&_rect]:fill-[var(--color-accent)]" />
          <h1 className="text-2xl sm:text-4xl font-bold mb-4 break-keep leading-tight">
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

      {/* Stats / Trust Section */}
      <section className="py-10 bg-[var(--color-primary-50)]">
        <div className="max-w-3xl mx-auto px-4">
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 sm:gap-6">
            <div className="flex flex-col items-center text-center p-4">
              <div className="w-10 h-10 rounded-full bg-blue-100 dark:bg-blue-900/30 flex items-center justify-center mb-2">
                <svg className="w-5 h-5 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" />
                </svg>
              </div>
              <p className="text-lg sm:text-xl font-bold text-[var(--color-text)]">44,097<span className="text-sm font-medium">개</span></p>
              <p className="text-xs text-[var(--color-text-secondary)]">의약품</p>
            </div>
            <div className="flex flex-col items-center text-center p-4">
              <div className="w-10 h-10 rounded-full bg-green-100 dark:bg-green-900/30 flex items-center justify-center mb-2">
                <svg className="w-5 h-5 text-green-600 dark:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
                </svg>
              </div>
              <p className="text-lg sm:text-xl font-bold text-[var(--color-text)]">44,551<span className="text-sm font-medium">개</span></p>
              <p className="text-xs text-[var(--color-text-secondary)]">건강기능식품</p>
            </div>
            <div className="flex flex-col items-center text-center p-4">
              <div className="w-10 h-10 rounded-full bg-amber-100 dark:bg-amber-900/30 flex items-center justify-center mb-2">
                <svg className="w-5 h-5 text-amber-600 dark:text-amber-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                </svg>
              </div>
              <p className="text-lg sm:text-xl font-bold text-[var(--color-text)]">12,502<span className="text-sm font-medium">건</span></p>
              <p className="text-xs text-[var(--color-text-secondary)]">상호작용 데이터</p>
            </div>
            <div className="flex flex-col items-center text-center p-4">
              <div className="w-10 h-10 rounded-full bg-teal-100 dark:bg-teal-900/30 flex items-center justify-center mb-2">
                <svg className="w-5 h-5 text-teal-600 dark:text-teal-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 013.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 010 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 010-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 013.138-3.138z" />
                </svg>
              </div>
              <p className="text-lg sm:text-xl font-bold text-[var(--color-text)]">식약처</p>
              <p className="text-xs text-[var(--color-text-secondary)]">공공데이터 기반</p>
            </div>
          </div>
        </div>
      </section>

      {/* Trust badges */}
      <section className="py-10 border-b border-gray-100 dark:border-[var(--color-border)]">
        <div className="max-w-3xl mx-auto px-4">
          <div className="grid grid-cols-3 gap-3 sm:gap-6 text-center">
            <div>
              <div className="w-12 h-12 mx-auto mb-2 rounded-full bg-[var(--color-primary-50)] flex items-center justify-center">
                <svg className="w-6 h-6 text-[var(--color-primary)]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                </svg>
              </div>
              <p className="text-sm font-semibold text-gray-900 dark:text-gray-100">식약처 공공데이터</p>
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-0.5">공식 데이터 기반</p>
            </div>
            <div>
              <div className="w-12 h-12 mx-auto mb-2 rounded-full bg-[var(--color-primary-50)] flex items-center justify-center">
                <svg className="w-6 h-6 text-[var(--color-primary)]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
              <p className="text-sm font-semibold text-gray-900 dark:text-gray-100">3초 확인</p>
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-0.5">빠른 상호작용 체크</p>
            </div>
            <div>
              <div className="w-12 h-12 mx-auto mb-2 rounded-full bg-[var(--color-primary-50)] flex items-center justify-center">
                <svg className="w-6 h-6 text-[var(--color-primary)]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <p className="text-sm font-semibold text-gray-900 dark:text-gray-100">완전 무료</p>
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-0.5">회원가입 없이 이용</p>
            </div>
          </div>
        </div>
      </section>

      {/* 홈 광고 */}
      <AdBanner slot="home-mid" format="auto" className="max-w-3xl mx-auto px-4" />

      {/* Features */}
      <section className="py-16">
        <div className="max-w-3xl mx-auto px-4">
          <h2 className="text-2xl font-bold text-center text-gray-900 dark:text-gray-100 mb-10">
            약잘알로 할 수 있는 것
          </h2>
          <div className="grid gap-3 sm:gap-6 grid-cols-2 sm:grid-cols-3">
            <Link href="/check" className="group block bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-4 sm:p-6 shadow-sm hover:shadow-md hover:border-[var(--color-primary-100)] transition-all">
              <div className="w-10 h-10 rounded-lg bg-blue-50 flex items-center justify-center mb-2 sm:mb-3 group-hover:bg-blue-100 transition-colors">
                <svg className="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
                </svg>
              </div>
              <h3 className="font-semibold text-gray-900 dark:text-gray-100 mb-1">상호작용 체크</h3>
              <p className="text-sm text-gray-500 dark:text-gray-400">복용 중인 약과 영양제의 상호작용을 확인하세요.</p>
            </Link>
            <Link href="/drugs" className="group block bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-4 sm:p-6 shadow-sm hover:shadow-md hover:border-[var(--color-primary-100)] transition-all">
              <div className="w-10 h-10 rounded-lg bg-rose-50 flex items-center justify-center mb-2 sm:mb-3 group-hover:bg-rose-100 transition-colors">
                <svg className="w-5 h-5 text-rose-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" />
                </svg>
              </div>
              <h3 className="font-semibold text-gray-900 dark:text-gray-100 mb-1">의약품 목록</h3>
              <p className="text-sm text-gray-500 dark:text-gray-400">44,000여 의약품의 효능, 부작용 정보를 확인하세요.</p>
            </Link>
            <Link href="/supplements" className="group block bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-4 sm:p-6 shadow-sm hover:shadow-md hover:border-[var(--color-primary-100)] transition-all">
              <div className="w-10 h-10 rounded-lg bg-green-50 flex items-center justify-center mb-2 sm:mb-3 group-hover:bg-green-100 transition-colors">
                <svg className="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
                </svg>
              </div>
              <h3 className="font-semibold text-gray-900 dark:text-gray-100 mb-1">건강기능식품</h3>
              <p className="text-sm text-gray-500 dark:text-gray-400">44,000여 건강기능식품의 성분, 기능성, 섭취방법을 확인하세요.</p>
            </Link>
            <Link href="/tips" className="group block bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-4 sm:p-6 shadow-sm hover:shadow-md hover:border-[var(--color-primary-100)] transition-all">
              <div className="w-10 h-10 rounded-lg bg-emerald-50 flex items-center justify-center mb-2 sm:mb-3 group-hover:bg-emerald-100 transition-colors">
                <svg className="w-5 h-5 text-emerald-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                </svg>
              </div>
              <h3 className="font-semibold text-gray-900 dark:text-gray-100 mb-1">건강팁</h3>
              <p className="text-sm text-gray-500 dark:text-gray-400">약과 영양제를 안전하게 복용하는 정보를 확인하세요.</p>
            </Link>
            <Link href="/cabinet" className="group block bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-4 sm:p-6 shadow-sm hover:shadow-md hover:border-[var(--color-primary-100)] transition-all">
              <div className="w-10 h-10 rounded-lg bg-amber-50 flex items-center justify-center mb-2 sm:mb-3 group-hover:bg-amber-100 transition-colors">
                <svg className="w-5 h-5 text-amber-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                </svg>
              </div>
              <h3 className="font-semibold text-gray-900 dark:text-gray-100 mb-1">내 복약함</h3>
              <p className="text-sm text-gray-500 dark:text-gray-400">복용 중인 약과 영양제를 관리하세요.</p>
            </Link>
          </div>
        </div>
      </section>

      {/* Popular Combinations */}
      <section className="py-16 bg-[var(--color-primary-50)]">
        <div className="max-w-3xl mx-auto px-4">
          <h2 className="text-2xl font-bold text-center text-[var(--color-text)] mb-2 flex items-center justify-center gap-2">
            <svg className="w-6 h-6 text-orange-500" fill="currentColor" viewBox="0 0 24 24">
              <path d="M13.5.67s.74 2.65.74 4.8c0 2.06-1.35 3.73-3.41 3.73-2.07 0-3.63-1.67-3.63-3.73l.03-.36C5.21 7.51 4 10.62 4 14c0 4.42 3.58 8 8 8s8-3.58 8-8C20 8.61 17.41 3.8 13.5.67zM11.71 19c-1.78 0-3.22-1.4-3.22-3.14 0-1.62 1.05-2.76 2.81-3.12 1.77-.36 3.6-1.21 4.62-2.58.39 1.29.59 2.65.59 4.04 0 2.65-2.15 4.8-4.8 4.8z" />
            </svg>
            자주 확인하는 조합
          </h2>
          <p className="text-center text-sm text-[var(--color-text-secondary)] mb-8">
            다른 사용자들이 많이 확인한 약물 조합
          </p>

          {/* Mobile: horizontal scroll, Desktop: grid */}
          <div className="flex sm:grid sm:grid-cols-4 gap-3 overflow-x-auto sm:overflow-visible pb-2 sm:pb-0 snap-x snap-mandatory sm:snap-none scrollbar-hide">
            {POPULAR_COMBOS.filter((combo) => comboUrls.has(combo.label)).map((combo) => (
              <Link
                key={combo.label}
                href={comboUrls.get(combo.label)!}
                className="group flex-shrink-0 w-40 sm:w-auto snap-start bg-[var(--color-surface)] border border-[var(--color-border)] rounded-xl p-3 sm:p-4 shadow-sm hover:shadow-md hover:border-[var(--color-primary-100)] transition-all"
              >
                <div className="flex items-center gap-1.5 mb-2">
                  <span className="inline-block px-2 py-0.5 text-xs font-medium rounded-full bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 truncate">
                    {combo.items[0]}
                  </span>
                  <span className="text-[var(--color-text-muted)] text-xs">+</span>
                  <span className="inline-block px-2 py-0.5 text-xs font-medium rounded-full bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300 truncate">
                    {combo.items[1]}
                  </span>
                </div>
                <p className="text-xs text-[var(--color-primary)] dark:text-[var(--color-accent)] font-medium group-hover:underline">
                  확인하기 →
                </p>
              </Link>
            ))}
          </div>
        </div>
      </section>

      {/* 신규 도구 */}
      <section className="py-16 bg-gray-50 dark:bg-gray-900">
        <div className="max-w-3xl mx-auto px-4">
          <h2 className="text-2xl font-bold text-center text-gray-900 dark:text-gray-100 mb-3">
            더 많은 약물 도구
          </h2>
          <p className="text-center text-sm text-gray-500 dark:text-gray-400 mb-10">
            약물 정보를 다양한 방법으로 검색하고 확인하세요
          </p>
          <div className="grid gap-3 sm:gap-4 grid-cols-2 sm:grid-cols-3">
            <Link href="/symptoms" className="group block bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-3 sm:p-5 shadow-sm hover:shadow-md hover:border-[var(--color-primary-100)] transition-all">
              <div className="w-9 h-9 rounded-lg bg-purple-50 flex items-center justify-center mb-2 group-hover:bg-purple-100 transition-colors">
                <svg className="w-5 h-5 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
              </div>
              <h3 className="font-semibold text-gray-900 dark:text-gray-100 text-sm mb-0.5">증상별 약물 검색</h3>
              <p className="text-xs text-gray-500 dark:text-gray-400">두통, 소화불량 등 증상으로 약 찾기</p>
            </Link>
            <Link href="/drugs/side-effects" className="group block bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-3 sm:p-5 shadow-sm hover:shadow-md hover:border-[var(--color-primary-100)] transition-all">
              <div className="w-9 h-9 rounded-lg bg-red-50 flex items-center justify-center mb-2 group-hover:bg-red-100 transition-colors">
                <svg className="w-5 h-5 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z" />
                </svg>
              </div>
              <h3 className="font-semibold text-gray-900 dark:text-gray-100 text-sm mb-0.5">부작용 역검색</h3>
              <p className="text-xs text-gray-500 dark:text-gray-400">부작용 키워드로 관련 약물 검색</p>
            </Link>
            <Link href="/drugs/identify" className="group block bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-3 sm:p-5 shadow-sm hover:shadow-md hover:border-[var(--color-primary-100)] transition-all">
              <div className="w-9 h-9 rounded-lg bg-cyan-50 flex items-center justify-center mb-2 group-hover:bg-cyan-100 transition-colors">
                <svg className="w-5 h-5 text-cyan-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                </svg>
              </div>
              <h3 className="font-semibold text-gray-900 dark:text-gray-100 text-sm mb-0.5">약 식별</h3>
              <p className="text-xs text-gray-500 dark:text-gray-400">색상, 모양, 각인으로 약 찾기</p>
            </Link>
            <Link href="/drugs/conditions" className="group block bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-3 sm:p-5 shadow-sm hover:shadow-md hover:border-[var(--color-primary-100)] transition-all">
              <div className="w-9 h-9 rounded-lg bg-orange-50 flex items-center justify-center mb-2 group-hover:bg-orange-100 transition-colors">
                <svg className="w-5 h-5 text-orange-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
              <h3 className="font-semibold text-gray-900 dark:text-gray-100 text-sm mb-0.5">질환별 주의사항</h3>
              <p className="text-xs text-gray-500 dark:text-gray-400">간질환, 당뇨 등 질환별 약물 경고</p>
            </Link>
            <Link href="/news" className="group block bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-3 sm:p-5 shadow-sm hover:shadow-md hover:border-[var(--color-primary-100)] transition-all">
              <div className="w-9 h-9 rounded-lg bg-indigo-50 flex items-center justify-center mb-2 group-hover:bg-indigo-100 transition-colors">
                <svg className="w-5 h-5 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z" />
                </svg>
              </div>
              <h3 className="font-semibold text-gray-900 dark:text-gray-100 text-sm mb-0.5">의약품 소식</h3>
              <p className="text-xs text-gray-500 dark:text-gray-400">최근 등록 의약품 및 안전 정보</p>
            </Link>
            <Link href="/professional" className="group block bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-3 sm:p-5 shadow-sm hover:shadow-md hover:border-[var(--color-primary-100)] transition-all">
              <div className="w-9 h-9 rounded-lg bg-slate-100 flex items-center justify-center mb-2 group-hover:bg-slate-200 transition-colors">
                <svg className="w-5 h-5 text-slate-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 013.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 010 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 010-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 013.138-3.138z" />
                </svg>
              </div>
              <h3 className="font-semibold text-gray-900 dark:text-gray-100 text-sm mb-0.5">전문가용 정보</h3>
              <p className="text-xs text-gray-500 dark:text-gray-400">의료 전문가를 위한 상세 약물 정보</p>
            </Link>
          </div>
        </div>
      </section>
    </>
  );
}
