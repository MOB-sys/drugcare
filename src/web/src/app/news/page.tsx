import type { Metadata } from "next";
import type { ReactNode } from "react";
import Link from "next/link";
import { getRecentDrugs } from "@/lib/api/drugs";
import { Breadcrumbs } from "@/components/common/Breadcrumbs";
import { AdBanner } from "@/components/ads/AdBanner";
import type { DrugSearchItem } from "@/types/drug";

export const revalidate = 86400; // ISR 24시간

export const metadata: Metadata = {
  title: "의약품 소식 | 약잘알",
  description:
    "최근 등록된 의약품과 약물 안전 정보를 확인하세요.",
  openGraph: {
    title: "의약품 소식 | 약잘알",
    description: "최근 등록된 의약품과 약물 안전 정보를 확인하세요.",
  },
};

/** 안전 정보 카드 데이터. */
const SAFETY_CARDS = [
  {
    title: "임산부 약물 안전",
    description: "임신 중 복용 시 주의해야 할 약물과 안전한 대안에 대해 알아보세요.",
    href: "/tips",
    icon: "pregnant",
    color: "bg-pink-50 text-pink-600 border-pink-100",
  },
  {
    title: "노인 다제 복용 주의",
    description: "65세 이상 어르신의 다제 복용 위험성과 주의사항을 확인하세요.",
    href: "/tips",
    icon: "elderly",
    color: "bg-amber-50 text-amber-600 border-amber-100",
  },
  {
    title: "계절별 상비약 가이드",
    description: "계절에 따라 준비해야 할 상비약과 올바른 보관 방법을 안내합니다.",
    href: "/tips",
    icon: "seasonal",
    color: "bg-sky-50 text-sky-600 border-sky-100",
  },
  {
    title: "건강기능식품 선택 가이드",
    description: "건강기능식품의 올바른 선택과 복용 방법에 대해 알아보세요.",
    href: "/supplements",
    icon: "supplement",
    color: "bg-emerald-50 text-emerald-600 border-emerald-100",
  },
];

const SAFETY_ICONS: Record<string, ReactNode> = {
  pregnant: (
    <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
    </svg>
  ),
  elderly: (
    <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
    </svg>
  ),
  seasonal: (
    <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
    </svg>
  ),
  supplement: (
    <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" />
    </svg>
  ),
};

export default async function NewsPage() {
  let recentDrugs: DrugSearchItem[] = [];
  try {
    recentDrugs = await getRecentDrugs(30, 20);
  } catch {
    // 에러 시 빈 목록
  }

  return (
    <>
      <Breadcrumbs
        items={[
          { label: "홈", href: "/" },
          { label: "의약품 소식" },
        ]}
      />

      <div className="max-w-5xl mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold text-[var(--color-primary)] mb-8">
          의약품 소식
        </h1>

        {/* 최근 등록 의약품 */}
        <section className="mb-12">
          <h2 className="text-xl font-semibold text-gray-800 mb-4 flex items-center gap-2">
            <svg className="w-5 h-5 text-[var(--color-primary)]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            최근 등록 의약품
          </h2>

          {recentDrugs.length === 0 ? (
            <p className="text-center py-8 text-gray-400 text-sm">
              최근 30일 이내 등록된 의약품이 없습니다.
            </p>
          ) : (
            <div className="grid gap-2 sm:grid-cols-2">
              {recentDrugs.map((drug) => (
                <Link
                  key={drug.id}
                  href={`/drugs/${drug.slug}`}
                  className="flex items-center gap-3 p-3 bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 hover:border-[var(--color-primary-100)] hover:shadow-sm transition-all"
                >
                  <div className="w-10 h-10 rounded-lg bg-[var(--color-primary-50)] flex items-center justify-center shrink-0">
                    <svg className="w-5 h-5 text-[var(--color-primary)]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" />
                    </svg>
                  </div>
                  <div className="min-w-0">
                    <p className="text-sm font-medium text-gray-900 truncate">
                      {drug.item_name}
                    </p>
                    {drug.entp_name && (
                      <p className="text-xs text-gray-500 truncate">{drug.entp_name}</p>
                    )}
                  </div>
                  {drug.etc_otc_code && (
                    <span className="ml-auto shrink-0 text-xs px-2 py-0.5 rounded-md bg-blue-50 text-blue-700">
                      {drug.etc_otc_code}
                    </span>
                  )}
                </Link>
              ))}
            </div>
          )}
        </section>

        <AdBanner slot="news-middle" format="horizontal" />

        {/* 약물 안전 정보 */}
        <section className="mt-8">
          <h2 className="text-xl font-semibold text-gray-800 mb-4 flex items-center gap-2">
            <svg className="w-5 h-5 text-[var(--color-primary)]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
            </svg>
            알아두면 좋은 약물 안전 정보
          </h2>

          <div className="grid gap-4 sm:grid-cols-2">
            {SAFETY_CARDS.map((card) => (
              <Link
                key={card.title}
                href={card.href}
                className={`block p-5 rounded-xl border ${card.color} hover:shadow-md transition-all`}
              >
                <div className="flex items-start gap-3">
                  <div className="shrink-0 mt-0.5">
                    {SAFETY_ICONS[card.icon]}
                  </div>
                  <div>
                    <h3 className="font-semibold mb-1">{card.title}</h3>
                    <p className="text-sm opacity-80">{card.description}</p>
                  </div>
                </div>
              </Link>
            ))}
          </div>
        </section>

        {/* 면책조항 */}
        <p className="text-xs text-gray-400 text-center mt-8">
          이 정보는 식약처 공공데이터를 기반으로 하며, 의사/약사의 전문적 판단을 대체하지 않습니다.
        </p>
      </div>
    </>
  );
}
