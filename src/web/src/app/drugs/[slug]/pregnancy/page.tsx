import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { getDrugBySlug, getAllDrugSlugs } from "@/lib/api/drugs";
import { Breadcrumbs } from "@/components/common/Breadcrumbs";
import { AdBanner } from "@/components/ads/AdBanner";
import { SITE_URL } from "@/lib/constants/site";
import type { DURSafetyItem } from "@/types/drug";

interface PageProps {
  params: Promise<{ slug: string }>;
}

/* ── ISR ────────────────────────────────────────── */

export const dynamicParams = true;
export const revalidate = 86400; // 24시간

export async function generateStaticParams() {
  // 빌드 시 생성하지 않고 요청 시 생성 (ISR)
  return [];
}

export async function generateMetadata({ params }: PageProps): Promise<Metadata> {
  const { slug } = await params;
  try {
    const drug = await getDrugBySlug(slug);
    const title = `${drug.item_name} 임신·수유 안전정보 — 약잘알`;
    const description = `${drug.item_name}의 임부 금기, 수유부 주의사항 등 임신·수유 중 복용 안전 정보를 확인하세요.`;
    return {
      title,
      description,
      openGraph: {
        title,
        description,
        type: "article",
        images: [
          {
            url: `${SITE_URL}/api/og?title=${encodeURIComponent(`${drug.item_name} 임신·수유 안전정보`)}&type=drug`,
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
      alternates: { canonical: `/drugs/${slug}/pregnancy` },
    };
  } catch {
    return { title: "임신·수유 안전정보" };
  }
}

/* ── Helpers ────────────────────────────────────── */

/** dur_safety에서 pregnancy 타입만 추출. */
function getPregnancyItems(durSafety: DURSafetyItem[] | null): DURSafetyItem[] {
  if (!durSafety) return [];
  return durSafety.filter((item) => item.dur_type === "pregnancy");
}

/** 텍스트에서 "수유" 키워드를 포함하는 문장을 추출. */
function extractBreastfeedingSentences(text: string | null): string[] {
  if (!text) return [];
  const sentences = text.split(/(?<=[.다])\s+/).filter(Boolean);
  return sentences.filter((s) => s.includes("수유"));
}

/** 텍스트에서 임부/임산부/임신/수유 관련 문장 추출 (일반 주의사항용). */
function extractPregnancyRelatedSentences(text: string | null): string[] {
  if (!text) return [];
  const keywords = ["임부", "임산부", "임신", "수유"];
  const sentences = text.split(/(?<=[.다])\s+/).filter(Boolean);
  return sentences.filter((s) => keywords.some((kw) => s.includes(kw)));
}

/* ── Page ───────────────────────────────────────── */

export default async function PregnancySafetyPage({ params }: PageProps) {
  const { slug } = await params;
  let drug;
  try {
    drug = await getDrugBySlug(slug);
  } catch {
    notFound();
  }

  const pregnancyItems = getPregnancyItems(drug.dur_safety);
  const breastfeedingSentences = [
    ...extractBreastfeedingSentences(drug.atpn_qesitm),
    ...extractBreastfeedingSentences(drug.atpn_warn_qesitm),
  ];
  const generalPrecautions = [
    ...extractPregnancyRelatedSentences(drug.atpn_qesitm),
    ...extractPregnancyRelatedSentences(drug.atpn_warn_qesitm),
  ];
  // 중복 제거 (수유부 문장은 일반 주의사항에서 제외)
  const breastfeedingSet = new Set(breastfeedingSentences);
  const uniqueGeneralPrecautions = generalPrecautions.filter(
    (s) => !breastfeedingSet.has(s),
  );

  const hasAnyInfo =
    pregnancyItems.length > 0 ||
    breastfeedingSentences.length > 0 ||
    uniqueGeneralPrecautions.length > 0;

  const jsonLd = {
    "@context": "https://schema.org",
    "@type": "MedicalWebPage",
    name: `${drug.item_name} 임신·수유 안전정보`,
    about: {
      "@type": "Drug",
      name: drug.item_name,
    },
    description: `${drug.item_name}의 임부 금기, 수유부 주의사항 등 임신·수유 중 복용 안전 정보`,
    url: `${SITE_URL}/drugs/${slug}/pregnancy`,
    lastReviewed: new Date().toISOString().split("T")[0],
    medicalAudience: {
      "@type": "MedicalAudience",
      audienceType: "Patient",
    },
  };

  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd).replace(/</g, '\\u003c') }}
      />

      <Breadcrumbs
        items={[
          { label: "홈", href: "/" },
          { label: "의약품", href: "/drugs" },
          { label: drug.item_name, href: `/drugs/${slug}` },
          { label: "임신·수유 안전정보" },
        ]}
      />

      <div className="max-w-3xl mx-auto px-4 py-6">
        {/* 헤더 */}
        <header className="mb-6">
          <h1 className="text-2xl font-bold text-[var(--color-primary)] mb-2 break-keep">
            {drug.item_name}
          </h1>
          <p className="text-lg text-gray-700 dark:text-gray-300">
            임신·수유 안전 정보
          </p>
        </header>

        {hasAnyInfo ? (
          <div className="space-y-6">
            {/* 임부 금기 정보 */}
            {pregnancyItems.length > 0 && (
              <section>
                <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-3 flex items-center gap-2">
                  <svg className="w-5 h-5 text-red-600" aria-hidden="true" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z" />
                  </svg>
                  임부 금기 정보
                </h2>
                <div className="rounded-lg border border-red-200 dark:border-red-800 bg-red-50 dark:bg-red-900/20 p-4">
                  <ul className="space-y-3">
                    {pregnancyItems.map((item, idx) => (
                      <li key={idx} className="text-sm leading-relaxed text-red-800 dark:text-red-200">
                        {item.ingr_name && (
                          <span className="font-semibold block text-red-900 dark:text-red-100">
                            [{item.ingr_name}]
                          </span>
                        )}
                        <span>
                          {item.prohibition_content || "임부에 대한 금기 사항이 있습니다."}
                        </span>
                        {item.remark && (
                          <span className="block text-xs mt-1 text-red-600 dark:text-red-300 opacity-80">
                            {item.remark}
                          </span>
                        )}
                      </li>
                    ))}
                  </ul>
                </div>
              </section>
            )}

            {/* 수유부 주의사항 */}
            {breastfeedingSentences.length > 0 && (
              <section>
                <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-3 flex items-center gap-2">
                  <svg className="w-5 h-5 text-orange-600" aria-hidden="true" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  수유부 주의사항
                </h2>
                <div className="rounded-lg border border-orange-200 dark:border-orange-800 bg-orange-50 dark:bg-orange-900/20 p-4">
                  <ul className="space-y-2">
                    {breastfeedingSentences.map((sentence, idx) => (
                      <li key={idx} className="text-sm leading-relaxed text-orange-800 dark:text-orange-200">
                        {sentence}
                      </li>
                    ))}
                  </ul>
                </div>
              </section>
            )}

            {/* 일반 주의사항 발췌 */}
            {uniqueGeneralPrecautions.length > 0 && (
              <section>
                <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-3 flex items-center gap-2">
                  <svg className="w-5 h-5 text-amber-600" aria-hidden="true" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                  관련 주의사항 발췌
                </h2>
                <div className="rounded-lg border border-amber-200 dark:border-amber-800 bg-amber-50 dark:bg-amber-900/20 p-4">
                  <ul className="space-y-2">
                    {uniqueGeneralPrecautions.map((sentence, idx) => (
                      <li key={idx} className="text-sm leading-relaxed text-amber-800 dark:text-amber-200">
                        {sentence}
                      </li>
                    ))}
                  </ul>
                </div>
              </section>
            )}
          </div>
        ) : (
          /* 정보 없음 */
          <div className="rounded-lg border border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800 p-6 text-center">
            <svg className="w-12 h-12 mx-auto text-gray-400 dark:text-gray-500 mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            <p className="text-gray-600 dark:text-gray-400 text-sm">
              이 약물에 대한 임신·수유 관련 안전 정보가 등록되어 있지 않습니다.
            </p>
          </div>
        )}

        {/* 약물 상세 페이지로 돌아가기 */}
        <div className="mt-8">
          <Link
            href={`/drugs/${slug}`}
            className="inline-flex items-center gap-1.5 text-sm text-[var(--color-primary)] hover:underline transition-colors"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
            {drug.item_name} 상세 정보로 돌아가기
          </Link>
        </div>

        {/* 광고 */}
        <AdBanner slot="drug-pregnancy-bottom" format="horizontal" />

        {/* 면책조항 */}
        <p className="text-xs text-gray-400 dark:text-gray-500 text-center mt-6">
          본 정보는 참고용이며, 의사/약사의 전문적 판단을 대체하지 않습니다.
          임신 중이거나 수유 중인 경우 반드시 담당 의사와 상담하세요.
        </p>
      </div>
    </>
  );
}
