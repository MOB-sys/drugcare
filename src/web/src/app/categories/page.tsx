import type { Metadata } from "next";
import Link from "next/link";
import { drugCategories } from "@/lib/data/drugCategories";
import { Breadcrumbs } from "@/components/common/Breadcrumbs";

const siteUrl = process.env.NEXT_PUBLIC_SITE_URL || "https://pillright.com";

export const metadata: Metadata = {
  title: "약물 분류별 가이드 — 진통제부터 안약까지",
  description:
    "진통소염제, 항생제, 혈압약, 당뇨약 등 12가지 주요 약물 분류별 복용 주의사항과 상호작용 정보를 확인하세요.",
  keywords: [
    "약물 분류",
    "약 종류",
    "진통제",
    "항생제",
    "혈압약",
    "당뇨약",
    "복용 주의사항",
  ],
  openGraph: {
    title: "약물 분류별 가이드 — 약잘알",
    description:
      "12가지 주요 약물 분류별 복용 주의사항과 상호작용 정보",
    type: "website",
    images: [
      {
        url: `${siteUrl}/api/og?title=${encodeURIComponent("약물 분류별 가이드")}&type=category`,
        width: 1200,
        height: 630,
        alt: "약물 분류별 가이드 — 약잘알",
      },
    ],
  },
};

export default function CategoriesPage() {
  return (
    <>
      <Breadcrumbs
        items={[
          { label: "홈", href: "/" },
          { label: "약물 분류" },
        ]}
      />

      <section className="max-w-4xl mx-auto px-4 py-6">
        <h1 className="text-2xl font-bold text-[var(--color-primary)] mb-2">
          약물 분류별 가이드
        </h1>
        <p className="text-gray-500 dark:text-gray-400 mb-8">
          주요 약물 분류별 특징, 대표 약물, 복용 시 주의사항을 확인하세요.
        </p>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {drugCategories.map((cat) => (
            <Link
              key={cat.slug}
              href={`/categories/${cat.slug}`}
              className="group block rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 p-5 shadow-sm hover:shadow-md hover:border-[var(--color-primary-200)] transition-all"
            >
              <div className="flex items-center gap-3 mb-3">
                <span className="inline-flex items-center justify-center w-10 h-10 rounded-lg bg-[var(--color-primary-50)] dark:bg-[var(--color-primary-900)] text-sm font-bold text-[var(--color-primary)]">
                  {cat.icon}
                </span>
                <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100 group-hover:text-[var(--color-primary)] transition-colors">
                  {cat.name}
                </h2>
              </div>
              <p className="text-sm text-gray-500 dark:text-gray-400 line-clamp-2 mb-3">
                {cat.description}
              </p>
              <p className="text-xs text-gray-400 dark:text-gray-500">
                대표 약물 {cat.examples.length}종 | 주의사항{" "}
                {cat.precautions.length}건
              </p>
            </Link>
          ))}
        </div>

        <p className="text-xs text-gray-400 dark:text-gray-500 text-center mt-8">
          이 정보는 일반적인 건강 정보이며, 의사/약사의 전문적 판단을 대체하지
          않습니다.
        </p>
      </section>
    </>
  );
}
