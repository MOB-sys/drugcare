import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { getSupplementBySlug, getRelatedSupplements } from "@/lib/api/supplements";
import { InfoSection } from "@/components/detail/InfoSection";
import { IngredientsTable } from "@/components/detail/IngredientsTable";
import { CheckCTA } from "@/components/detail/CheckCTA";
import { AddToCabinetButton } from "@/components/detail/AddToCabinetButton";
import { AdBanner } from "@/components/ads/AdBanner";
import { ReviewSection } from "@/components/review/ReviewSection";
import { Breadcrumbs } from "@/components/common/Breadcrumbs";
import { DataSource } from "@/components/common/DataSource";
import { KakaoShareButton } from "@/components/common/KakaoShareButton";
import { TableOfContents } from "@/components/common/TableOfContents";
import type { TocItem } from "@/components/common/TableOfContents";
import type { IngredientInfo } from "@/types/drug";
import { SITE_URL } from "@/lib/constants/site";

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
    const supp = await getSupplementBySlug(slug);
    const title = `${supp.product_name} 기능성·성분·섭취방법`;
    const description = supp.functionality
      ? `${supp.product_name} — ${supp.functionality.slice(0, 120)}`
      : `${supp.product_name} 건강기능식품 상세 정보를 확인하세요.`;
    const siteUrl = SITE_URL;
    return {
      title,
      description,
      openGraph: {
        title,
        description,
        type: "article",
        images: [
          {
            url: `${siteUrl}/api/og?title=${encodeURIComponent(supp.product_name)}&type=supplement`,
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
      alternates: { canonical: `/supplements/${slug}` },
    };
  } catch {
    return { title: "영양제 정보" };
  }
}

/** JSONB 성분 데이터를 IngredientInfo[]로 정규화. */
function normalizeIngredients(raw: Record<string, unknown>[] | null): IngredientInfo[] {
  if (!raw) return [];
  return raw.map((item) => ({
    name: String(item.name ?? item.ingredient_name ?? ""),
    amount: item.amount != null ? String(item.amount) : null,
    unit: item.unit != null ? String(item.unit) : null,
  }));
}

/* ── Page ───────────────────────────────────────── */

export default async function SupplementDetailPage({ params }: PageProps) {
  const { slug } = await params;
  let supp;
  try {
    supp = await getSupplementBySlug(slug);
  } catch {
    notFound();
  }

  const ingredients = normalizeIngredients(supp.ingredients);
  const relatedSupps = await getRelatedSupplements(supp.category, slug);

  const jsonLd = {
    "@context": "https://schema.org",
    "@type": "Product",
    name: supp.product_name,
    manufacturer: supp.company ? { "@type": "Organization", name: supp.company } : undefined,
    description: supp.functionality ?? undefined,
    category: supp.category ?? "건강기능식품",
  };

  /* FAQ JSON-LD — 상세 정보를 Q&A로 구조화 */
  const faqEntries: { question: string; answer: string }[] = [];
  if (supp.functionality) faqEntries.push({ question: `${supp.product_name}의 기능성은?`, answer: supp.functionality });
  if (supp.main_ingredient) faqEntries.push({ question: `${supp.product_name}의 주성분은?`, answer: supp.main_ingredient });
  if (supp.intake_method) faqEntries.push({ question: `${supp.product_name}의 섭취방법은?`, answer: supp.intake_method });
  if (supp.precautions) faqEntries.push({ question: `${supp.product_name} 섭취 시 주의사항은?`, answer: supp.precautions });

  const faqJsonLd = faqEntries.length > 0 ? {
    "@context": "https://schema.org",
    "@type": "FAQPage",
    mainEntity: faqEntries.map((e) => ({
      "@type": "Question",
      name: e.question,
      acceptedAnswer: { "@type": "Answer", text: e.answer },
    })),
  } : null;

  /* 목차 아이템 구성 */
  const tocItems: TocItem[] = [
    supp.functionality && { id: "functionality", label: "기능성" },
    supp.main_ingredient && { id: "main-ingredient", label: "주성분" },
    ingredients.length > 0 && { id: "ingredients", label: "성분정보" },
    supp.intake_method && { id: "intake", label: "섭취방법" },
    supp.precautions && { id: "precautions", label: "섭취 시 주의사항" },
  ].filter(Boolean) as TocItem[];

  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd).replace(/</g, '\\u003c') }}
      />
      {faqJsonLd && (
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{ __html: JSON.stringify(faqJsonLd).replace(/</g, '\\u003c') }}
        />
      )}

      <Breadcrumbs
        items={[
          { label: "홈", href: "/" },
          { label: "건강기능식품", href: "/supplements" },
          { label: supp.product_name },
        ]}
      />

      <div className="max-w-5xl mx-auto px-4 py-6">
        <div className="lg:grid lg:grid-cols-[1fr_220px] lg:gap-8">
          {/* ── 메인 콘텐츠 ── */}
          <article className="min-w-0">
            {/* 헤더 */}
            <div className="mb-6">
              <h1 className="text-2xl font-bold text-[var(--color-primary)] mb-2 break-keep">{supp.product_name}</h1>
              <div className="flex flex-wrap gap-2 text-sm mb-3">
                {supp.company && (
                  <span className="px-2 py-0.5 rounded-md bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300">{supp.company}</span>
                )}
                {supp.category && (
                  <span className="px-2 py-0.5 rounded-md bg-emerald-50 text-emerald-700">{supp.category}</span>
                )}
                {supp.registration_no && (
                  <span className="px-2 py-0.5 rounded-md bg-gray-100 dark:bg-gray-700 text-gray-500 dark:text-gray-400">{supp.registration_no}</span>
                )}
              </div>
              <DataSource source="식약처 건강기능식품 정보" />
            </div>

            {/* 정보 섹션 */}
            <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 px-6 divide-y divide-gray-100 dark:divide-gray-700 shadow-sm">
              <InfoSection id="functionality" title="기능성" content={supp.functionality} />
              <InfoSection id="main-ingredient" title="주성분" content={supp.main_ingredient} />

              {ingredients.length > 0 && (
                <div id="ingredients" className="scroll-mt-24">
                  <IngredientsTable ingredients={ingredients} />
                </div>
              )}

              <InfoSection id="intake" title="섭취방법" content={supp.intake_method} />
              <InfoSection id="precautions" title="섭취 시 주의사항" content={supp.precautions} />
            </div>

            {/* CTA */}
            <CheckCTA itemType="supplement" itemId={supp.id} itemName={supp.product_name} />
            <div className="pb-4 flex flex-wrap items-center gap-3">
              <AddToCabinetButton itemType="supplement" itemId={supp.id} itemName={supp.product_name} />
              <KakaoShareButton
                title={`${supp.product_name} 기능성·성분·섭취방법`}
                description={supp.functionality ? supp.functionality.slice(0, 100) : `${supp.product_name} 건강기능식품 상세 정보를 확인하세요.`}
                imageUrl={`${SITE_URL}/api/og?title=${encodeURIComponent(supp.product_name)}&type=supplement`}
                pageUrl={`${SITE_URL}/supplements/${slug}`}
              />
            </div>

            {/* 관련 건강기능식품 */}
            {relatedSupps.length > 0 && (
              <section className="mt-8">
                <h2 className="text-lg font-semibold text-[var(--color-primary)] mb-3">관련 건강기능식품</h2>
                <div className="grid gap-2 sm:grid-cols-2">
                  {relatedSupps.map((rs) => (
                    <Link
                      key={rs.id}
                      href={`/supplements/${rs.slug}`}
                      className="flex items-center gap-3 p-3 bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 hover:border-[var(--color-primary-100)] hover:shadow-sm transition-all"
                    >
                      <div className="w-10 h-10 rounded-lg bg-emerald-50 flex items-center justify-center shrink-0">
                        <svg className="w-5 h-5 text-emerald-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
                        </svg>
                      </div>
                      <div className="min-w-0">
                        <p className="text-sm font-medium text-gray-900 dark:text-gray-100 truncate">{rs.product_name}</p>
                        {rs.company && <p className="text-xs text-gray-500 dark:text-gray-400 truncate">{rs.company}</p>}
                      </div>
                    </Link>
                  ))}
                </div>
              </section>
            )}

            {/* 리뷰 */}
            <ReviewSection itemType="supplement" itemId={supp.id} />

            {/* 광고 */}
            <AdBanner slot="supplement-detail-bottom" format="horizontal" />

            {/* 면책조항 */}
            <p className="text-xs text-gray-400 dark:text-gray-500 text-center mt-4">
              이 정보는 식약처 공공데이터를 기반으로 하며, 의사/약사의 전문적 판단을 대체하지 않습니다.
            </p>
          </article>

          {/* ── 사이드바 (PC only) ── */}
          <aside className="hidden lg:block">
            <div className="space-y-6">
              {/* 목차 */}
              <TableOfContents items={tocItems} />

              {/* 사이드바 광고 */}
              <AdBanner slot="supplement-detail-sidebar" format="rectangle" />

              {/* 관련 링크 */}
              <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-4">
                <p className="text-xs font-semibold text-gray-400 dark:text-gray-500 uppercase tracking-wider mb-2">바로가기</p>
                <ul className="space-y-1.5">
                  <li>
                    <Link href="/check" className="text-sm text-gray-600 dark:text-gray-400 hover:text-[var(--color-primary)] transition-colors">
                      상호작용 체크
                    </Link>
                  </li>
                  <li>
                    <Link href="/supplements" className="text-sm text-gray-600 dark:text-gray-400 hover:text-[var(--color-primary)] transition-colors">
                      건강기능식품 목록
                    </Link>
                  </li>
                  <li>
                    <Link href="/cabinet" className="text-sm text-gray-600 dark:text-gray-400 hover:text-[var(--color-primary)] transition-colors">
                      내 복약함
                    </Link>
                  </li>
                </ul>
              </div>
            </div>
          </aside>
        </div>
      </div>
    </>
  );
}
