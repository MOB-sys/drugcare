import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import {
  getIngredientBySlug,
  getAllIngredientSlugs,
  getRelatedIngredients,
  categoryConfig,
} from "@/lib/data/ingredients";
import { AdBanner } from "@/components/ads/AdBanner";
import { Breadcrumbs } from "@/components/common/Breadcrumbs";
import { SITE_URL } from "@/lib/constants/site";

interface PageProps {
  params: Promise<{ slug: string }>;
}

/* ── SSG ────────────────────────────────────────── */

export function generateStaticParams() {
  return getAllIngredientSlugs().map((slug) => ({ slug }));
}

export async function generateMetadata({ params }: PageProps): Promise<Metadata> {
  const { slug } = await params;
  const ingredient = getIngredientBySlug(slug);
  if (!ingredient) return { title: "성분 가이드" };

  const title = `${ingredient.name}(${ingredient.nameEn}) — 효과, 부작용, 주의사항`;
  const description = ingredient.summary;
  const siteUrl = SITE_URL;

  return {
    title,
    description,
    keywords: [
      ingredient.name,
      ingredient.nameEn,
      `${ingredient.name} 부작용`,
      `${ingredient.name} 상호작용`,
      `${ingredient.name} 복용법`,
    ],
    openGraph: {
      title,
      description,
      type: "article",
      images: [
        {
          url: `${siteUrl}/api/og?title=${encodeURIComponent(ingredient.name)}&type=ingredient`,
          width: 1200,
          height: 630,
          alt: title,
        },
      ],
    },
    twitter: {
      card: "summary_large_image",
      title,
      description,
    },
  };
}

/* ── Page ───────────────────────────────────────── */

export default async function IngredientDetailPage({ params }: PageProps) {
  const { slug } = await params;
  const ingredient = getIngredientBySlug(slug);
  if (!ingredient) notFound();

  const related = getRelatedIngredients(ingredient.category, slug, 4);
  const config = categoryConfig[ingredient.category];

  /* JSON-LD: MedicalWebPage */
  const jsonLd = {
    "@context": "https://schema.org",
    "@type": "MedicalWebPage",
    name: `${ingredient.name}(${ingredient.nameEn})`,
    description: ingredient.summary,
    about: {
      "@type": "Drug",
      name: ingredient.name,
      alternateName: ingredient.nameEn,
    },
    author: { "@type": "Organization", name: "약잘알" },
    publisher: { "@type": "Organization", name: "약잘알" },
    lastReviewed: new Date().toISOString().split("T")[0],
  };

  /* FAQ JSON-LD */
  const faqJsonLd = {
    "@context": "https://schema.org",
    "@type": "FAQPage",
    mainEntity: [
      {
        "@type": "Question",
        name: `${ingredient.name}의 주요 부작용은 무엇인가요?`,
        acceptedAnswer: {
          "@type": "Answer",
          text: ingredient.sideEffects.join(", "),
        },
      },
      {
        "@type": "Question",
        name: `${ingredient.name}과 상호작용 주의가 필요한 약물은?`,
        acceptedAnswer: {
          "@type": "Answer",
          text: ingredient.interactions.join(" "),
        },
      },
      {
        "@type": "Question",
        name: `${ingredient.name} 복용 시 주의할 점은?`,
        acceptedAnswer: {
          "@type": "Answer",
          text: ingredient.tips.join(" "),
        },
      },
    ],
  };

  /* 설명 문단 분리 */
  const descriptionParagraphs = ingredient.description
    .split("\n\n")
    .map((p) => p.trim())
    .filter(Boolean);

  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
      />
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(faqJsonLd) }}
      />

      <Breadcrumbs
        items={[
          { label: "홈", href: "/" },
          { label: "성분 가이드", href: "/ingredients" },
          { label: ingredient.name },
        ]}
      />

      <article className="max-w-3xl mx-auto px-4 py-6">
        {/* ── 헤더 ── */}
        <div className="mb-8">
          <div className="flex items-center gap-2 mb-3">
            <span
              className={`px-2.5 py-0.5 rounded-full text-xs font-medium ${config.bgClass} ${config.textClass}`}
            >
              {config.label}
            </span>
          </div>
          <h1 className="text-2xl font-bold text-[var(--color-primary)] mb-1 break-keep">
            {ingredient.name}
          </h1>
          <p className="text-sm text-gray-400 dark:text-gray-500 mb-3">
            {ingredient.nameEn}
          </p>
          <p className="text-gray-600 dark:text-gray-400 leading-relaxed">
            {ingredient.summary}
          </p>
        </div>

        {/* ── 이 성분이란? ── */}
        <section className="mb-8">
          <h2 className="text-xl font-bold text-[var(--color-primary)] mb-3 flex items-center gap-2">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            이 성분이란?
          </h2>
          <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-5">
            {descriptionParagraphs.map((para, i) => (
              <p key={i} className="text-gray-700 dark:text-gray-300 leading-relaxed mb-3 last:mb-0">
                {para}
              </p>
            ))}
          </div>
        </section>

        {/* ── 포함된 대표 약물 ── */}
        <section className="mb-8">
          <h2 className="text-xl font-bold text-[var(--color-primary)] mb-3 flex items-center gap-2">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" />
            </svg>
            포함된 대표 약물
          </h2>
          <div className="flex flex-wrap gap-2">
            {ingredient.commonDrugs.map((drug) => (
              <span
                key={drug}
                className="inline-flex items-center px-3 py-1.5 rounded-lg text-sm font-medium bg-blue-50 dark:bg-blue-950 text-blue-700 dark:text-blue-300 border border-blue-100 dark:border-blue-900"
              >
                {drug}
              </span>
            ))}
          </div>
        </section>

        {/* ── 주요 부작용 ── */}
        <section className="mb-8">
          <h2 className="text-xl font-bold text-[var(--color-primary)] mb-3 flex items-center gap-2">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4.5c-.77-.833-2.694-.833-3.464 0L3.34 16.5c-.77.833.192 2.5 1.732 2.5z" />
            </svg>
            주요 부작용
          </h2>
          <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-5">
            <ul className="space-y-2">
              {ingredient.sideEffects.map((effect, i) => (
                <li key={i} className="flex items-start gap-2 text-gray-700 dark:text-gray-300">
                  <span className="mt-1.5 w-1.5 h-1.5 rounded-full bg-red-400 shrink-0" />
                  <span>{effect}</span>
                </li>
              ))}
            </ul>
          </div>
        </section>

        {/* ── 상호작용 주의 ── */}
        <section className="mb-8">
          <h2 className="text-xl font-bold text-[var(--color-primary)] mb-3 flex items-center gap-2">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4" />
            </svg>
            상호작용 주의
          </h2>
          <div className="space-y-3">
            {ingredient.interactions.map((interaction, i) => (
              <div
                key={i}
                className="bg-amber-50 dark:bg-amber-950 border border-amber-200 dark:border-amber-800 rounded-xl p-4"
              >
                <p className="text-sm text-amber-900 dark:text-amber-200">{interaction}</p>
              </div>
            ))}
          </div>
        </section>

        {/* ── 복용 팁 ── */}
        <section className="mb-8">
          <h2 className="text-xl font-bold text-[var(--color-primary)] mb-3 flex items-center gap-2">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            복용 팁
          </h2>
          <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-5">
            <ul className="space-y-3">
              {ingredient.tips.map((tip, i) => (
                <li key={i} className="flex items-start gap-3 text-gray-700 dark:text-gray-300">
                  <span className="mt-0.5 flex items-center justify-center w-5 h-5 rounded-full bg-[var(--color-primary-50)] text-[var(--color-primary)] text-xs font-semibold shrink-0">
                    {i + 1}
                  </span>
                  <span>{tip}</span>
                </li>
              ))}
            </ul>
          </div>
        </section>

        {/* ── 면책조항 배너 ── */}
        <div className="mb-8 bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-xl p-5">
          <div className="flex items-start gap-3">
            <svg className="w-5 h-5 text-gray-400 mt-0.5 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <div>
              <p className="text-sm font-semibold text-gray-600 dark:text-gray-400 mb-1">
                안내 사항
              </p>
              <p className="text-xs text-gray-500 dark:text-gray-500 leading-relaxed">
                이 페이지의 정보는 일반적인 건강 정보 제공 목적으로 작성되었으며,
                의사/약사의 전문적 판단을 대체하지 않습니다. 약물 복용에 관한
                결정은 반드시 담당 의료진과 상담 후 내려주세요. 개인의 건강 상태에
                따라 적용이 달라질 수 있습니다.
              </p>
            </div>
          </div>
        </div>

        {/* ── 관련 성분 ── */}
        {related.length > 0 && (
          <section className="mb-8">
            <h2 className="text-lg font-semibold text-[var(--color-primary)] mb-3">
              같은 카테고리 성분
            </h2>
            <div className="grid gap-2 sm:grid-cols-2">
              {related.map((rel) => (
                <Link
                  key={rel.slug}
                  href={`/ingredients/${rel.slug}`}
                  className="flex items-center gap-3 p-3 bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 hover:border-[var(--color-primary-100)] hover:shadow-sm transition-all"
                >
                  <div className="w-10 h-10 rounded-lg bg-[var(--color-primary-50)] flex items-center justify-center shrink-0">
                    <svg className="w-5 h-5 text-[var(--color-primary)]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" />
                    </svg>
                  </div>
                  <div className="min-w-0">
                    <p className="text-sm font-medium text-gray-900 dark:text-gray-100 truncate">
                      {rel.name}
                    </p>
                    <p className="text-xs text-gray-500 dark:text-gray-400 truncate">
                      {rel.nameEn}
                    </p>
                  </div>
                </Link>
              ))}
            </div>
          </section>
        )}

        {/* ── CTA ── */}
        <div className="mt-8 bg-[var(--color-primary-50)] border border-[var(--color-primary-100)] rounded-xl p-6 text-center">
          <p className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-2">
            {ingredient.name}이(가) 포함된 약, 다른 약과 함께 먹어도 될까?
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

        {/* 광고 */}
        <AdBanner slot="ingredient-detail-bottom" format="auto" />

        {/* 면책조항 하단 */}
        <p className="text-xs text-gray-400 text-center mt-6">
          이 정보는 일반적인 건강 정보이며, 의사/약사의 전문적 판단을 대체하지
          않습니다.
        </p>
      </article>
    </>
  );
}
