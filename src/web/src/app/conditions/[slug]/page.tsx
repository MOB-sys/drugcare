import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { searchDrugsByCondition } from "@/lib/api/drugs";
import {
  getConditionBySlug,
  getAllConditionSlugs,
} from "@/lib/data/conditions";
import { AdBanner } from "@/components/ads/AdBanner";
import { Breadcrumbs } from "@/components/common/Breadcrumbs";
import { SITE_URL } from "@/lib/constants/site";
import type { DrugConditionItem } from "@/types/drug";

interface PageProps {
  params: Promise<{ slug: string }>;
}

/* -- SSG ------------------------------------------------ */

export const revalidate = 86400;

export const dynamicParams = true;

export function generateStaticParams() {
  // 빌드 시 생성하지 않고 첫 요청 시 ISR로 생성 (빌드 환경에서 API 접근 불가 대비)
  return [];
}

export async function generateMetadata({
  params,
}: PageProps): Promise<Metadata> {
  const { slug } = await params;
  const condition = getConditionBySlug(slug);
  if (!condition) return { title: "질환별 주의 약물" };

  const title = `${condition.label} 관련 주의 약물 — 약잘알`;
  const description = condition.seoDescription;
  const siteUrl = SITE_URL;

  return {
    title,
    description,
    keywords: [
      condition.label,
      `${condition.label} 약물`,
      `${condition.label} 주의사항`,
      `${condition.label} 복용 주의`,
      "약물 주의사항",
    ],
    openGraph: {
      title,
      description,
      type: "article",
      images: [
        {
          url: `${siteUrl}/api/og?title=${encodeURIComponent(`${condition.icon} ${condition.label} 주의 약물`)}&type=condition`,
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

/* -- helpers -------------------------------------------- */

/** 주의사항 텍스트에서 키워드 주변을 잘라낸다. */
function extractSnippet(text: string, keyword: string, radius = 80): string {
  const idx = text.indexOf(keyword);
  if (idx < 0) return text.slice(0, radius * 2);
  const start = Math.max(0, idx - radius);
  const end = Math.min(text.length, idx + keyword.length + radius);
  const prefix = start > 0 ? "..." : "";
  const suffix = end < text.length ? "..." : "";
  return `${prefix}${text.slice(start, end)}${suffix}`;
}

/** API에서 약물 목록을 안전하게 가져온다. 빌드 시 API 불가하면 빈 배열. */
async function fetchDrugsForCondition(
  keyword: string,
): Promise<{ items: DrugConditionItem[]; total: number }> {
  try {
    const res = await searchDrugsByCondition(keyword, 1, 50);
    return { items: res.items, total: res.total };
  } catch (error) {
    console.error(
      `[conditions/${keyword}] Failed to fetch drugs:`,
      error,
    );
    return { items: [], total: 0 };
  }
}

/* -- Page ----------------------------------------------- */

export default async function ConditionDetailPage({ params }: PageProps) {
  const { slug } = await params;
  const condition = getConditionBySlug(slug);
  if (!condition) notFound();

  const { items: drugs, total } = await fetchDrugsForCondition(
    condition.keyword,
  );

  /* JSON-LD: MedicalWebPage */
  const jsonLd = {
    "@context": "https://schema.org",
    "@type": "MedicalWebPage",
    name: `${condition.label} 관련 주의 약물`,
    description: condition.seoDescription,
    about: {
      "@type": "MedicalCondition",
      name: condition.label,
    },
    author: { "@type": "Organization", name: "약잘알" },
    publisher: { "@type": "Organization", name: "약잘알" },
    lastReviewed: new Date().toISOString().split("T")[0],
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
          { label: "질환별 주의 약물", href: "/conditions" },
          { label: condition.label },
        ]}
      />

      <article className="max-w-3xl mx-auto px-4 py-6">
        {/* -- 헤더 -- */}
        <div className="flex items-center gap-4 mb-2">
          <span
            className="inline-flex items-center justify-center w-14 h-14 rounded-2xl bg-[var(--color-primary-50)] dark:bg-[var(--color-primary-900)] text-2xl"
            role="img"
            aria-label={condition.label}
          >
            {condition.icon}
          </span>
          <h1 className="text-2xl font-bold text-[var(--color-primary)] break-keep">
            {condition.label} 관련 주의 약물
          </h1>
        </div>
        <p className="text-gray-600 dark:text-gray-400 leading-relaxed mb-6 ml-[4.5rem]">
          {condition.seoDescription}
        </p>

        {/* -- 결과 요약 -- */}
        <div className="flex items-center justify-between mb-4">
          <p className="text-sm text-gray-500 dark:text-gray-400">
            총{" "}
            <span className="font-semibold text-[var(--color-primary)]">
              {total.toLocaleString()}
            </span>
            건의 주의 약물
          </p>
          {total > 50 && (
            <Link
              href={`/drugs/conditions?q=${encodeURIComponent(condition.keyword)}`}
              className="text-xs text-[var(--color-primary)] hover:underline"
            >
              전체 보기
            </Link>
          )}
        </div>

        {/* -- 약물 목록 -- */}
        {drugs.length === 0 ? (
          <div className="text-center py-12 text-gray-400 dark:text-gray-500">
            <p className="mb-2">현재 표시할 약물 데이터가 없습니다.</p>
            <p className="text-xs">
              데이터가 업데이트되면 자동으로 표시됩니다.
            </p>
          </div>
        ) : (
          <ul className="space-y-3">
            {drugs.map((drug) => {
              const cautionText =
                drug.atpn_warn_qesitm || drug.atpn_qesitm || "";
              const snippet = cautionText
                ? extractSnippet(cautionText, condition.keyword)
                : "";

              return (
                <li key={drug.id}>
                  <Link
                    href={`/drugs/${drug.slug}`}
                    className="block p-4 border border-gray-200 dark:border-gray-700 rounded-xl hover:border-[var(--color-primary-100)] hover:bg-[var(--color-primary-50)]/30 dark:hover:bg-[var(--color-primary-900)]/30 transition-colors"
                  >
                    <div className="flex items-start gap-3">
                      {drug.item_image && (
                        <img
                          src={drug.item_image}
                          alt={drug.item_name}
                          className="w-12 h-12 object-contain rounded-lg bg-gray-50 dark:bg-gray-800 shrink-0"
                          loading="lazy"
                        />
                      )}
                      <div className="min-w-0 flex-1">
                        <h3 className="text-sm font-semibold text-gray-900 dark:text-white truncate">
                          {drug.item_name}
                        </h3>
                        {drug.entp_name && (
                          <p className="text-xs text-gray-400 dark:text-gray-500 mt-0.5">
                            {drug.entp_name}
                          </p>
                        )}
                        {snippet && (
                          <p className="text-xs text-gray-500 dark:text-gray-400 mt-1 leading-relaxed">
                            {snippet
                              .split(condition.keyword)
                              .map((part, i, arr) =>
                                i < arr.length - 1 ? (
                                  <span key={i}>
                                    {part}
                                    <mark className="bg-orange-100 dark:bg-orange-900 text-orange-800 dark:text-orange-200 rounded px-0.5">
                                      {condition.keyword}
                                    </mark>
                                  </span>
                                ) : (
                                  <span key={i}>{part}</span>
                                ),
                              )}
                          </p>
                        )}
                      </div>
                    </div>
                  </Link>
                </li>
              );
            })}
          </ul>
        )}

        <AdBanner slot="condition-detail-mid" format="auto" />

        {/* -- 다른 질환 보기 -- */}
        <div className="mt-8 text-center">
          <Link
            href="/conditions"
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
                d="M4 6h16M4 10h16M4 14h16M4 18h16"
              />
            </svg>
            다른 질환별 주의 약물 보기
          </Link>
        </div>

        {/* -- CTA -- */}
        <div className="mt-8 bg-[var(--color-primary-50)] dark:bg-[var(--color-primary-900)] border border-[var(--color-primary-100)] dark:border-[var(--color-primary-800)] rounded-xl p-6 text-center">
          <p className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-2">
            복용 중인 약물의 상호작용이 궁금하세요?
          </p>
          <p className="text-sm text-gray-500 dark:text-gray-400 mb-4">
            약잘알에서 3초 만에 약물 간 상호작용을 체크할 수 있습니다.
          </p>
          <Link
            href="/check"
            className="inline-block px-6 py-3 rounded-xl text-white font-semibold bg-[var(--color-primary)] hover:bg-[var(--color-primary-dark)] shadow-md transition-all"
          >
            상호작용 체크하러 가기
          </Link>
        </div>

        {/* -- 면책조항 -- */}
        <div className="mt-8 p-4 bg-amber-50 dark:bg-amber-950 border border-amber-200 dark:border-amber-800 rounded-xl">
          <div className="flex items-start gap-3">
            <svg
              className="w-5 h-5 text-amber-500 mt-0.5 shrink-0"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4.5c-.77-.833-2.694-.833-3.464 0L3.34 16.5c-.77.833.192 2.5 1.732 2.5z"
              />
            </svg>
            <div>
              <p className="text-sm font-semibold text-amber-800 dark:text-amber-300 mb-1">
                안내 사항
              </p>
              <p className="text-xs text-amber-700 dark:text-amber-400 leading-relaxed">
                이 페이지의 정보는 일반적인 건강 정보 제공 목적으로
                작성되었으며, 의사/약사의 전문적 판단을 대체하지 않습니다. 약물
                복용에 관한 결정은 반드시 담당 의료진과 상담 후 내려주세요.
              </p>
            </div>
          </div>
        </div>

        <p className="text-xs text-gray-400 dark:text-gray-500 text-center mt-6">
          이 정보는 일반적인 건강 정보이며, 의사/약사의 전문적 판단을 대체하지
          않습니다.
        </p>
      </article>
    </>
  );
}
