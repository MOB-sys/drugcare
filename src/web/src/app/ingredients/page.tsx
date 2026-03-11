import type { Metadata } from "next";
import Link from "next/link";
import {
  getIngredientsByCategory,
  categoryConfig,
  categoryOrder,
} from "@/lib/data/ingredients";
import { Breadcrumbs } from "@/components/common/Breadcrumbs";
import { AdBanner } from "@/components/ads/AdBanner";
import { SITE_URL } from "@/lib/constants/site";

const siteUrl = SITE_URL;

export const metadata: Metadata = {
  title: "주요 성분 가이드",
  description:
    "아세트아미노펜, 이부프로펜, 비타민D 등 자주 접하는 약물·영양제 성분의 효과, 부작용, 주의사항을 알기 쉽게 설명합니다.",
  alternates: { canonical: "/ingredients" },
  openGraph: {
    title: "주요 성분 가이드 — 약잘알",
    description:
      "자주 접하는 약물·영양제 성분의 효과, 부작용, 주의사항을 알기 쉽게 설명합니다.",
    type: "website",
    images: [
      {
        url: `${siteUrl}/api/og?title=${encodeURIComponent("주요 성분 가이드")}&type=ingredient`,
        width: 1200,
        height: 630,
        alt: "주요 성분 가이드 — 약잘알",
      },
    ],
  },
};

export default function IngredientsPage() {
  const grouped = getIngredientsByCategory();

  return (
    <>
      <Breadcrumbs
        items={[
          { label: "홈", href: "/" },
          { label: "성분 가이드" },
        ]}
      />

      <section className="max-w-4xl mx-auto px-4 py-6">
        <h1 className="text-2xl font-bold text-[var(--color-primary)] mb-2">
          주요 성분 가이드
        </h1>
        <p className="text-gray-500 dark:text-gray-400 mb-8">
          자주 접하는 약물·영양제 성분의 효과, 부작용, 주의사항을 알기 쉽게
          설명합니다.
        </p>

        {categoryOrder.map((cat) => {
          const items = grouped[cat];
          if (!items || items.length === 0) return null;
          const config = categoryConfig[cat];

          return (
            <div key={cat} className="mb-10">
              <h2 className="text-lg font-semibold text-gray-800 dark:text-gray-200 mb-4 flex items-center gap-2">
                <span
                  className={`inline-block px-2.5 py-0.5 rounded-full text-xs font-medium ${config.bgClass} ${config.textClass}`}
                >
                  {config.label}
                </span>
              </h2>

              <div className="grid gap-3 sm:grid-cols-2">
                {items.map((ingredient) => (
                  <Link
                    key={ingredient.slug}
                    href={`/ingredients/${ingredient.slug}`}
                    className="group block p-4 bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 hover:border-[var(--color-primary-100)] hover:shadow-md transition-all"
                  >
                    <div className="flex items-start justify-between gap-2 mb-2">
                      <div>
                        <h3 className="font-semibold text-gray-900 dark:text-gray-100 group-hover:text-[var(--color-primary)] transition-colors">
                          {ingredient.name}
                        </h3>
                        <p className="text-xs text-gray-400 dark:text-gray-500">
                          {ingredient.nameEn}
                        </p>
                      </div>
                      <span
                        className={`shrink-0 px-2 py-0.5 rounded-full text-xs font-medium ${config.bgClass} ${config.textClass}`}
                      >
                        {config.label}
                      </span>
                    </div>
                    <p className="text-sm text-gray-600 dark:text-gray-400 line-clamp-2">
                      {ingredient.summary}
                    </p>
                  </Link>
                ))}
              </div>
            </div>
          );
        })}

        {/* 광고 */}
        <AdBanner slot="ingredients-list-bottom" format="auto" />

        {/* CTA */}
        <div className="mt-8 bg-[var(--color-primary-50)] border border-[var(--color-primary-100)] rounded-xl p-6 text-center">
          <p className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-2">
            복용 중인 약·영양제, 함께 먹어도 괜찮을까?
          </p>
          <p className="text-sm text-gray-500 dark:text-gray-400 mb-4">
            약잘알에서 3초 만에 상호작용을 체크할 수 있습니다.
          </p>
          <Link
            href="/check"
            className="inline-block px-6 py-3 rounded-xl text-white font-semibold bg-[var(--color-primary)] hover:bg-[var(--color-primary-dark)] shadow-md transition-all"
          >
            상호작용 체크하러 가기
          </Link>
        </div>

        {/* 면책조항 */}
        <p className="text-xs text-gray-400 dark:text-gray-500 text-center mt-6">
          이 정보는 일반적인 건강 정보이며, 의사/약사의 전문적 판단을 대체하지
          않습니다.
        </p>
      </section>
    </>
  );
}
