import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import {
  getCategoryBySlug,
  getAllCategorySlugs,
} from "@/lib/data/drugCategories";
import { AdBanner } from "@/components/ads/AdBanner";
import { Breadcrumbs } from "@/components/common/Breadcrumbs";
import { SITE_URL } from "@/lib/constants/site";

interface PageProps {
  params: Promise<{ slug: string }>;
}

/* -- SSG ------------------------------------------------ */

export function generateStaticParams() {
  return getAllCategorySlugs().map((slug) => ({ slug }));
}

export async function generateMetadata({
  params,
}: PageProps): Promise<Metadata> {
  const { slug } = await params;
  const cat = getCategoryBySlug(slug);
  if (!cat) return { title: "약물 분류" };

  const siteUrl = SITE_URL;
  return {
    title: `${cat.name} — 대표 약물과 복용 주의사항`,
    description: cat.description,
    keywords: [cat.name, "약물 분류", "복용 주의사항", ...cat.examples.slice(0, 3)],
    openGraph: {
      title: `${cat.name} — 약잘알`,
      description: cat.description,
      type: "article",
      images: [
        {
          url: `${siteUrl}/api/og?title=${encodeURIComponent(cat.name)}&type=category`,
          width: 1200,
          height: 630,
          alt: cat.name,
        },
      ],
    },
  };
}

/* -- Page ----------------------------------------------- */

export default async function CategoryDetailPage({ params }: PageProps) {
  const { slug } = await params;
  const cat = getCategoryBySlug(slug);
  if (!cat) notFound();

  const jsonLd = {
    "@context": "https://schema.org",
    "@type": "MedicalWebPage",
    name: cat.name,
    description: cat.description,
    publisher: { "@type": "Organization", name: "약잘알" },
  };

  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
      />

      <Breadcrumbs
        items={[
          { label: "홈", href: "/" },
          { label: "약물 분류", href: "/categories" },
          { label: cat.name },
        ]}
      />

      <article className="max-w-3xl mx-auto px-4 py-6">
        {/* 헤더 */}
        <div className="flex items-center gap-4 mb-4">
          <span className="inline-flex items-center justify-center w-14 h-14 rounded-2xl bg-[var(--color-primary-50)] dark:bg-[var(--color-primary-900)] text-xl font-bold text-[var(--color-primary)]">
            {cat.icon}
          </span>
          <h1 className="text-2xl font-bold text-[var(--color-primary)] break-keep">
            {cat.name}
          </h1>
        </div>

        <p className="text-gray-700 dark:text-gray-300 leading-relaxed mb-8">
          {cat.description}
        </p>

        {/* 대표 약물 */}
        <section className="mb-8">
          <h2 className="text-xl font-bold text-[var(--color-primary)] mb-4">
            대표 약물
          </h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
            {cat.examples.map((ex) => (
              <div
                key={ex}
                className="flex items-center gap-2 rounded-lg border border-gray-100 dark:border-gray-700 bg-gray-50 dark:bg-gray-800 px-4 py-3 text-sm text-gray-700 dark:text-gray-300"
              >
                <span className="w-1.5 h-1.5 rounded-full bg-[var(--color-primary)] shrink-0" />
                {ex}
              </div>
            ))}
          </div>
        </section>

        {/* 주의사항 */}
        <section className="mb-8">
          <h2 className="text-xl font-bold text-[var(--color-primary)] mb-4">
            복용 시 주의사항
          </h2>
          <ul className="space-y-3">
            {cat.precautions.map((p, i) => (
              <li
                key={i}
                className="flex gap-3 rounded-lg bg-amber-50 dark:bg-amber-950 border border-amber-100 dark:border-amber-900 px-4 py-3 text-sm text-gray-700 dark:text-gray-300"
              >
                <span className="text-amber-500 font-bold shrink-0">
                  {i + 1}.
                </span>
                {p}
              </li>
            ))}
          </ul>
        </section>

        {/* 광고 */}
        <AdBanner slot="category-detail-bottom" format="auto" />

        {/* CTA */}
        <div className="mt-8 bg-[var(--color-primary-50)] dark:bg-[var(--color-primary-900)] border border-[var(--color-primary-100)] dark:border-[var(--color-primary-800)] rounded-xl p-6 text-center">
          <p className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-2">
            이 분류의 약물 검색하기
          </p>
          <p className="text-sm text-gray-500 dark:text-gray-400 mb-4">
            약잘알에서 {cat.name} 관련 약물을 검색하고 상호작용을 확인하세요.
          </p>
          <Link
            href={`/drugs?q=${encodeURIComponent(cat.name)}`}
            className="inline-block px-6 py-3 rounded-xl text-white font-semibold bg-[var(--color-primary)] hover:bg-[var(--color-primary-dark)] shadow-md transition-all"
          >
            {cat.name} 검색하기
          </Link>
        </div>

        {/* 면책조항 */}
        <p className="text-xs text-gray-400 dark:text-gray-500 text-center mt-6">
          이 정보는 일반적인 건강 정보이며, 의사/약사의 전문적 판단을 대체하지
          않습니다.
        </p>
      </article>
    </>
  );
}
