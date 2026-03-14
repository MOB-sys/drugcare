import type { Metadata } from "next";
import dynamic from "next/dynamic";
import { SafeImage } from "@/components/common/SafeImage";
import Link from "next/link";
import { notFound } from "next/navigation";
import { getDrugBySlug, getRelatedDrugs } from "@/lib/api/drugs";
import { InfoSection } from "@/components/detail/InfoSection";
import { IngredientsTable } from "@/components/detail/IngredientsTable";
import { DURSafetySection } from "@/components/detail/DURSafetySection";
import { DosageGuide } from "@/components/detail/DosageGuide";
import { FoodInteractionSection } from "@/components/detail/FoodInteractionSection";
import { FallbackInfoSection } from "@/components/detail/FallbackInfoSection";
import { IngredientGuideSection } from "@/components/detail/IngredientGuideSection";
import { CategoryInfoSection } from "@/components/detail/CategoryInfoSection";
import { CheckCTA } from "@/components/detail/CheckCTA";
import { AddToCabinetButton } from "@/components/detail/AddToCabinetButton";
import { AdBanner } from "@/components/ads/AdBanner";
import { Breadcrumbs } from "@/components/common/Breadcrumbs";
import { DataSource } from "@/components/common/DataSource";
import { KakaoShareButton } from "@/components/common/KakaoShareButton";
import { TableOfContents } from "@/components/common/TableOfContents";
import type { TocItem } from "@/components/common/TableOfContents";
import { RelatedTips } from "@/components/drug/RelatedTips";
import { buildDrugFAQItems, buildFAQJsonLd } from "@/lib/faq";
import { SITE_URL } from "@/lib/constants/site";
import { DetailViewTracker } from "@/components/common/DetailViewTracker";
import { buildDrugFallbackContent } from "@/lib/utils/drugFallbackContent";

/* ── Below-fold 클라이언트 컴포넌트 lazy loading ── */
const ReviewSection = dynamic(
  () => import("@/components/review/ReviewSection").then((m) => ({ default: m.ReviewSection })),
  { loading: () => <div className="h-48 animate-pulse bg-gray-100 dark:bg-gray-800 rounded-xl mt-8" /> },
);
const DrugFAQ = dynamic(
  () => import("@/components/drug/DrugFAQ").then((m) => ({ default: m.DrugFAQ })),
  { loading: () => <div className="h-32 animate-pulse bg-gray-100 dark:bg-gray-800 rounded-xl mt-8" /> },
);

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
    const title = `${drug.item_name} 효능·용법·상호작용`;
    const fallback = buildDrugFallbackContent(drug);
    const description = drug.efcy_qesitm
      ? `${drug.item_name} — ${drug.efcy_qesitm.slice(0, 120)}`
      : fallback.overview
        ? `${drug.item_name} — ${fallback.overview.slice(0, 120)}`
        : fallback.category
          ? `${drug.item_name}은(는) ${fallback.category.name} 계열 의약품입니다. 효능, 용법, 부작용, 상호작용 정보를 확인하세요.`
          : `${drug.item_name} 의약품 상세 정보 — 효능, 용법, 부작용, 상호작용을 확인하세요.`;
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
            url: `${siteUrl}/api/og?title=${encodeURIComponent(drug.item_name)}&type=drug`,
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
      alternates: { canonical: `/drugs/${slug}` },
    };
  } catch {
    return { title: "약물 정보" };
  }
}

/* ── Page ───────────────────────────────────────── */

export default async function DrugDetailPage({ params }: PageProps) {
  const { slug } = await params;
  let drug;
  try {
    drug = await getDrugBySlug(slug);
  } catch {
    notFound();
  }

  let relatedDrugs: Awaited<ReturnType<typeof getRelatedDrugs>> = [];
  try {
    relatedDrugs = await getRelatedDrugs(drug.class_no, slug);
  } catch {
    // 관련 약물 로드 실패 시 빈 배열로 대체 — 메인 콘텐츠 표시에 영향 없음
  }

  const fallback = buildDrugFallbackContent(drug);

  const otcLabel =
    drug.etc_otc_code === "일반의약품"
      ? "일반의약품"
      : drug.etc_otc_code === "전문의약품"
        ? "전문의약품"
        : drug.etc_otc_code;

  const jsonLd = {
    "@context": "https://schema.org",
    "@type": "Drug",
    name: drug.item_name,
    manufacturer: drug.entp_name ? { "@type": "Organization", name: drug.entp_name } : undefined,
    description: drug.efcy_qesitm ?? fallback.overview ?? undefined,
    administrationRoute: drug.use_method_qesitm ?? undefined,
    warning: drug.atpn_warn_qesitm ?? undefined,
  };

  /* Product JSON-LD — Google Merchant / Rich Results 지원 */
  const productJsonLd: Record<string, unknown> = {
    "@context": "https://schema.org",
    "@type": "Product",
    name: drug.item_name,
    category: "의약품",
  };
  if (drug.efcy_qesitm) productJsonLd.description = drug.efcy_qesitm;
  else if (fallback.overview) productJsonLd.description = fallback.overview;
  if (drug.item_image) productJsonLd.image = drug.item_image;
  if (drug.entp_name) productJsonLd.brand = { "@type": "Brand", name: drug.entp_name };

  /* FAQ — 상세 정보를 Q&A로 구조화 (UI accordion + JSON-LD) */
  const faqSourceFields = {
    drugName: drug.item_name,
    efcyQesitm: drug.efcy_qesitm,
    seQesitm: drug.se_qesitm,
    atpnQesitm: drug.atpn_qesitm,
    intrcQesitm: drug.intrc_qesitm,
    depositMethodQesitm: drug.deposit_method_qesitm,
  };
  const baseFaqItems = buildDrugFAQItems(faqSourceFields);
  const faqItems = [...baseFaqItems, ...fallback.additionalFAQs];
  const faqJsonLd = buildFAQJsonLd(faqSourceFields);

  /* 목차 아이템 구성 — 내용이 있는 섹션만 (폴백 포함) */
  const tocItems: TocItem[] = [
    (drug.efcy_qesitm || fallback.overview) && { id: "efficacy", label: "효능·효과" },
    drug.use_method_qesitm && { id: "usage", label: "용법·용량" },
    drug.ingredients?.length && { id: "ingredients", label: "성분정보" },
    fallback.matchedIngredients.length > 0 && { id: "ingredient-guides", label: "성분 가이드" },
    drug.atpn_warn_qesitm && { id: "warnings", label: "주의사항 (경고)" },
    drug.atpn_qesitm && { id: "precautions", label: "주의사항" },
    (drug.intrc_qesitm || fallback.fallbackInteractions) && { id: "interactions", label: "상호작용" },
    drug.intrc_qesitm && { id: "food-interactions", label: "음식 상호작용" },
    (drug.se_qesitm || fallback.fallbackSideEffects) && { id: "side-effects", label: "부작용" },
    drug.dur_safety?.length && { id: "dur-safety", label: "DUR 안전성" },
    fallback.category && { id: "category-info", label: "분류 정보" },
    drug.deposit_method_qesitm && { id: "storage", label: "보관방법" },
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
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(productJsonLd).replace(/</g, '\\u003c') }}
      />

      <DetailViewTracker type="drug" id={drug.id} name={drug.item_name} />

      <Breadcrumbs
        items={[
          { label: "홈", href: "/" },
          { label: "의약품", href: "/drugs" },
          { label: drug.item_name },
        ]}
      />

      <div className="max-w-5xl mx-auto px-4 py-6">
        <div className="lg:grid lg:grid-cols-[1fr_220px] lg:gap-8">
          {/* ── 메인 콘텐츠 ── */}
          <article className="min-w-0">
            {/* 헤더 */}
            <div className="flex gap-6 mb-6">
              {drug.item_image && (
                <SafeImage
                  src={drug.item_image}
                  alt={drug.item_name}
                  width={128}
                  height={128}
                  priority
                  sizes="128px"
                  className="rounded-xl object-contain bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 shadow-sm shrink-0"
                />
              )}
              <div className="min-w-0">
                <h1 className="text-2xl font-bold text-[var(--color-primary)] mb-2 break-keep">{drug.item_name}</h1>
                <div className="flex flex-wrap gap-2 text-sm mb-3">
                  {drug.entp_name && (
                    <span className="px-2 py-0.5 rounded-md bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300">{drug.entp_name}</span>
                  )}
                  {otcLabel && (
                    <span className="px-2 py-0.5 rounded-md bg-blue-50 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300">{otcLabel}</span>
                  )}
                  {drug.class_no && (
                    <span className="px-2 py-0.5 rounded-md bg-gray-100 dark:bg-gray-700 text-gray-500 dark:text-gray-400">분류 {drug.class_no}</span>
                  )}
                </div>
                <DataSource source="식약처 의약품안전나라" />
              </div>
            </div>

            {/* 정보 섹션 */}
            <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 px-6 divide-y divide-gray-100 dark:divide-gray-700 shadow-sm">
              <InfoSection id="efficacy" title="효능·효과" content={drug.efcy_qesitm} />
              {!drug.efcy_qesitm && fallback.overview && (
                <FallbackInfoSection id="efficacy" title="효능·효과 (일반 정보)" content={fallback.overview} />
              )}
              {drug.use_method_qesitm ? (
                <DosageGuide id="usage" content={drug.use_method_qesitm} />
              ) : null}

              {drug.ingredients && drug.ingredients.length > 0 && (
                <div id="ingredients" className="scroll-mt-24">
                  <IngredientsTable ingredients={drug.ingredients} />
                </div>
              )}

              {fallback.matchedIngredients.length > 0 && (
                <div id="ingredient-guides" className="scroll-mt-24">
                  <IngredientGuideSection matchedIngredients={fallback.matchedIngredients} />
                </div>
              )}

              <InfoSection id="warnings" title="주의사항 (경고)" content={drug.atpn_warn_qesitm} />
              <InfoSection id="precautions" title="주의사항" content={drug.atpn_qesitm} />
              <InfoSection id="interactions" title="상호작용" content={drug.intrc_qesitm} />
              {!drug.intrc_qesitm && fallback.fallbackInteractions && (
                <FallbackInfoSection id="interactions" title="상호작용 (일반 정보)" content={fallback.fallbackInteractions} />
              )}
              <FoodInteractionSection intrcText={drug.intrc_qesitm} />
              <InfoSection id="side-effects" title="부작용" content={drug.se_qesitm} />
              {!drug.se_qesitm && fallback.fallbackSideEffects && (
                <FallbackInfoSection id="side-effects" title="부작용 (일반 정보)" content={fallback.fallbackSideEffects} />
              )}
              {drug.se_qesitm && (
                <div className="px-0 pb-2 -mt-2">
                  <Link
                    href={`/drugs/${slug}/side-effects`}
                    className="inline-flex items-center gap-1 text-sm text-[var(--color-primary)] hover:underline"
                  >
                    부작용 자세히 보기
                    <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                    </svg>
                  </Link>
                </div>
              )}

              {drug.dur_safety && drug.dur_safety.length > 0 && (
                <DURSafetySection items={drug.dur_safety} />
              )}

              {/* 임신·수유 안전정보 링크 — DUR pregnancy 데이터 또는 텍스트에 임부/수유 키워드가 있을 때 */}
              {(drug.dur_safety?.some((d) => d.dur_type === "pregnancy") ||
                /임부|임산부|임신|수유/.test(`${drug.atpn_qesitm ?? ""}${drug.atpn_warn_qesitm ?? ""}`)) && (
                <div className="py-4">
                  <Link
                    href={`/drugs/${slug}/pregnancy`}
                    className="flex items-center gap-3 p-4 rounded-lg border border-pink-200 dark:border-pink-800 bg-pink-50 dark:bg-pink-900/20 hover:border-pink-300 dark:hover:border-pink-700 hover:shadow-sm transition-all group"
                  >
                    <span className="flex items-center justify-center w-9 h-9 rounded-full bg-pink-100 dark:bg-pink-800 text-pink-600 dark:text-pink-300 shrink-0">
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z" />
                      </svg>
                    </span>
                    <div className="min-w-0 flex-1">
                      <p className="text-sm font-semibold text-pink-800 dark:text-pink-200">임신·수유 안전정보</p>
                      <p className="text-xs text-pink-600 dark:text-pink-400">임부 금기, 수유부 주의사항을 확인하세요</p>
                    </div>
                    <svg className="w-5 h-5 text-pink-400 dark:text-pink-500 group-hover:translate-x-0.5 transition-transform shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                    </svg>
                  </Link>
                </div>
              )}

              {fallback.category && (
                <div id="category-info" className="scroll-mt-24">
                  <CategoryInfoSection category={fallback.category} />
                </div>
              )}

              <InfoSection id="storage" title="보관방법" content={drug.deposit_method_qesitm} />
            </div>

            {/* CTA */}
            <CheckCTA itemType="drug" itemId={drug.id} itemName={drug.item_name} />
            <div className="pb-4 flex flex-wrap items-center gap-3">
              <AddToCabinetButton itemType="drug" itemId={drug.id} itemName={drug.item_name} />
              <KakaoShareButton
                title={`${drug.item_name} 효능·용법·상호작용`}
                description={drug.efcy_qesitm ? drug.efcy_qesitm.slice(0, 100) : `${drug.item_name} 의약품 상세 정보를 확인하세요.`}
                imageUrl={`${SITE_URL}/api/og?title=${encodeURIComponent(drug.item_name)}&type=drug`}
                pageUrl={`${SITE_URL}/drugs/${slug}`}
              />
            </div>

            {/* 관련 의약품 */}
            {relatedDrugs.length > 0 && (
              <section className="mt-8">
                <h2 className="text-lg font-semibold text-[var(--color-primary)] mb-3">관련 의약품</h2>
                <div className="grid gap-2 sm:grid-cols-2">
                  {relatedDrugs.map((rd) => (
                    <Link
                      key={rd.id}
                      href={`/drugs/${rd.slug}`}
                      className="flex items-center gap-3 p-3 bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 hover:border-[var(--color-primary-100)] hover:shadow-sm transition-all"
                    >
                      {rd.item_image ? (
                        <SafeImage
                          src={rd.item_image}
                          alt={rd.item_name}
                          width={40}
                          height={40}
                          className="rounded-lg object-contain bg-white dark:bg-gray-800 border border-gray-100 dark:border-gray-700 shrink-0"
                        />
                      ) : (
                        <div className="w-10 h-10 rounded-lg bg-[var(--color-primary-50)] flex items-center justify-center shrink-0">
                          <svg className="w-5 h-5 text-[var(--color-primary)]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" />
                          </svg>
                        </div>
                      )}
                      <div className="min-w-0">
                        <p className="text-sm font-medium text-gray-900 dark:text-gray-100 truncate">{rd.item_name}</p>
                        {rd.entp_name && <p className="text-xs text-gray-500 dark:text-gray-400 truncate">{rd.entp_name}</p>}
                      </div>
                    </Link>
                  ))}
                </div>
              </section>
            )}

            {/* FAQ */}
            <DrugFAQ items={faqItems} />

            {/* 관련 건강팁 */}
            <RelatedTips drugName={drug.item_name} classNo={drug.class_no} />

            {/* 리뷰 */}
            <ReviewSection itemType="drug" itemId={drug.id} />

            {/* 광고 */}
            <AdBanner slot="drug-detail-bottom" format="horizontal" />

            {/* 전문가용 링크 */}
            <div className="text-center mt-4">
              <Link
                href={`/professional/drugs/${slug}`}
                className="text-xs text-gray-500 dark:text-gray-400 hover:text-[var(--color-primary)] underline underline-offset-2 transition-colors"
              >
                전문가용 상세 정보 보기
              </Link>
            </div>

            {/* 면책조항 */}
            <p className="text-xs text-gray-400 dark:text-gray-500 text-center mt-2">
              이 정보는 식약처 공공데이터를 기반으로 하며, 의사/약사의 전문적 판단을 대체하지 않습니다.
            </p>
          </article>

          {/* ── 사이드바 (PC only) ── */}
          <aside className="hidden lg:block">
            <div className="space-y-6">
              {/* 목차 */}
              <TableOfContents items={tocItems} />

              {/* 사이드바 광고 */}
              <AdBanner slot="drug-detail-sidebar" format="rectangle" />

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
                    <Link href="/drugs" className="text-sm text-gray-600 dark:text-gray-400 hover:text-[var(--color-primary)] transition-colors">
                      의약품 목록
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
