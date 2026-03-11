import type { Metadata } from "next";
import Link from "next/link";
import { CONDITIONS } from "@/lib/data/conditions";
import { AdBanner } from "@/components/ads/AdBanner";
import { Breadcrumbs } from "@/components/common/Breadcrumbs";
import { SITE_URL } from "@/lib/constants/site";

export const revalidate = 86400;

export const metadata: Metadata = {
  title: "질환별 주의 약물 목록 — 약잘알",
  description:
    "간질환, 당뇨, 고혈압, 임부, 수유부 등 20가지 질환·상태별로 복용 시 주의가 필요한 의약품을 확인하세요.",
  keywords: [
    "질환별 약물",
    "주의 약물",
    "간질환 약",
    "당뇨 약",
    "고혈압 약",
    "임산부 약",
    "복용 주의사항",
  ],
  openGraph: {
    title: "질환별 주의 약물 목록 — 약잘알",
    description:
      "20가지 질환·상태별로 복용 시 주의가 필요한 의약품을 한눈에 확인하세요.",
    type: "website",
    images: [
      {
        url: `${SITE_URL}/api/og?title=${encodeURIComponent("질환별 주의 약물")}&type=conditions`,
        width: 1200,
        height: 630,
        alt: "질환별 주의 약물 목록",
      },
    ],
  },
};

export default function ConditionsIndexPage() {
  const jsonLd = {
    "@context": "https://schema.org",
    "@type": "CollectionPage",
    name: "질환별 주의 약물 목록",
    description:
      "20가지 질환·상태별로 복용 시 주의가 필요한 의약품 목록 페이지입니다.",
    publisher: { "@type": "Organization", name: "약잘알" },
    mainEntity: {
      "@type": "ItemList",
      numberOfItems: CONDITIONS.length,
      itemListElement: CONDITIONS.map((cond, i) => ({
        "@type": "ListItem",
        position: i + 1,
        name: `${cond.label} 관련 주의 약물`,
        url: `${SITE_URL}/conditions/${cond.slug}`,
      })),
    },
  };

  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify(jsonLd).replace(/</g, "\\u003c"),
        }}
      />

      <Breadcrumbs
        items={[
          { label: "홈", href: "/" },
          { label: "질환별 주의 약물" },
        ]}
      />

      <section className="max-w-4xl mx-auto px-4 py-6">
        <h1 className="text-2xl font-bold text-[var(--color-primary)] mb-2">
          질환별 주의 약물
        </h1>
        <p className="text-gray-500 dark:text-gray-400 mb-8 leading-relaxed">
          질환이나 상태를 선택하면 해당 조건에서 복용 시 주의가 필요한 의약품
          목록을 확인할 수 있습니다.
        </p>

        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3">
          {CONDITIONS.map((cond) => (
            <Link
              key={cond.slug}
              href={`/conditions/${cond.slug}`}
              className="group flex flex-col items-center gap-2 p-4 border border-gray-200 dark:border-gray-700 rounded-xl hover:border-[var(--color-primary-100)] hover:bg-[var(--color-primary-50)]/30 dark:hover:bg-[var(--color-primary-900)]/30 transition-colors text-center"
            >
              <span className="text-3xl" role="img" aria-label={cond.label}>
                {cond.icon}
              </span>
              <h2 className="text-sm font-semibold text-gray-900 dark:text-white group-hover:text-[var(--color-primary)] transition-colors">
                {cond.label}
              </h2>
              <p className="text-xs text-gray-400 dark:text-gray-500 leading-snug">
                {cond.description}
              </p>
            </Link>
          ))}
        </div>

        {/* 동적 검색 링크 */}
        <div className="mt-8 text-center">
          <Link
            href="/drugs/conditions"
            className="inline-flex items-center gap-2 text-sm text-[var(--color-primary)] hover:underline"
          >
            <svg
              className="w-4 h-4"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
              />
            </svg>
            다른 질환 키워드로 검색하기
          </Link>
        </div>

        <AdBanner slot="conditions-index-bottom" format="auto" />

        {/* 면책조항 */}
        <div className="mt-8 p-4 bg-amber-50 dark:bg-amber-950 border border-amber-200 dark:border-amber-800 rounded-xl">
          <p className="text-xs text-amber-700 dark:text-amber-300 leading-relaxed">
            질환별 주의사항은 참고용이며, 복용 전 반드시 의사/약사와 상담하세요.
            이 서비스는 의사/약사의 전문적 판단을 대체하지 않습니다.
          </p>
        </div>
      </section>
    </>
  );
}
