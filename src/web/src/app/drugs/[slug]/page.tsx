import type { Metadata } from "next";
import { SafeImage } from "@/components/common/SafeImage";
import Link from "next/link";
import { notFound } from "next/navigation";
import { getDrugBySlug, getAllDrugSlugs, getRelatedDrugs } from "@/lib/api/drugs";
import { InfoSection } from "@/components/detail/InfoSection";
import { IngredientsTable } from "@/components/detail/IngredientsTable";
import { DURSafetySection } from "@/components/detail/DURSafetySection";
import { DosageGuide } from "@/components/detail/DosageGuide";
import { FoodInteractionSection } from "@/components/detail/FoodInteractionSection";
import { CheckCTA } from "@/components/detail/CheckCTA";
import { AddToCabinetButton } from "@/components/detail/AddToCabinetButton";
import { AdBanner } from "@/components/ads/AdBanner";
import { ReviewSection } from "@/components/review/ReviewSection";
import { Breadcrumbs } from "@/components/common/Breadcrumbs";
import { DataSource } from "@/components/common/DataSource";
import { KakaoShareButton } from "@/components/common/KakaoShareButton";
import { TableOfContents } from "@/components/common/TableOfContents";
import type { TocItem } from "@/components/common/TableOfContents";
import { DrugFAQ } from "@/components/drug/DrugFAQ";
import { RelatedTips } from "@/components/drug/RelatedTips";
import { buildDrugFAQItems, buildFAQJsonLd } from "@/lib/faq";

interface PageProps {
  params: Promise<{ slug: string }>;
}

/* ── SSG ────────────────────────────────────────── */

export async function generateStaticParams() {
  try {
    const slugs = await getAllDrugSlugs();
    return slugs.map((slug) => ({ slug }));
  } catch (error) {
    console.error("[generateStaticParams:drugs] Failed to fetch drug slugs:", error);
    return [];
  }
}

export async function generateMetadata({ params }: PageProps): Promise<Metadata> {
  const { slug } = await params;
  try {
    const drug = await getDrugBySlug(slug);
    const title = `${drug.item_name} 효능·용법·상호작용`;
    const description = drug.efcy_qesitm
      ? `${drug.item_name} — ${drug.efcy_qesitm.slice(0, 120)}`
      : `${drug.item_name} 의약품 상세 정보를 확인하세요.`;
    const siteUrl = process.env.NEXT_PUBLIC_SITE_URL || "https://pillright.com";
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

  const relatedDrugs = await getRelatedDrugs(drug.class_no, slug);

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
    description: drug.efcy_qesitm ?? undefined,
    administrationRoute: drug.use_method_qesitm ?? undefined,
    warning: drug.atpn_warn_qesitm ?? undefined,
  };

  /* FAQ — 상세 정보를 Q&A로 구조화 (UI accordion + JSON-LD) */
  const faqSourceFields = {
    drugName: drug.item_name,
    efcyQesitm: drug.efcy_qesitm,
    seQesitm: drug.se_qesitm,
    atpnQesitm: drug.atpn_qesitm,
    intrcQesitm: drug.intrc_qesitm,
    depositMethodQesitm: drug.deposit_method_qesitm,
  };
  const faqItems = buildDrugFAQItems(faqSourceFields);
  const faqJsonLd = buildFAQJsonLd(faqSourceFields);

  /* 목차 아이템 구성 — 내용이 있는 섹션만 */
  const tocItems: TocItem[] = [
    drug.efcy_qesitm && { id: "efficacy", label: "효능·효과" },
    drug.use_method_qesitm && { id: "usage", label: "용법·용량" },
    drug.ingredients?.length && { id: "ingredients", label: "성분정보" },
    drug.atpn_warn_qesitm && { id: "warnings", label: "주의사항 (경고)" },
    drug.atpn_qesitm && { id: "precautions", label: "주의사항" },
    drug.intrc_qesitm && { id: "interactions", label: "상호작용" },
    drug.intrc_qesitm && { id: "food-interactions", label: "음식 상호작용" },
    drug.se_qesitm && { id: "side-effects", label: "부작용" },
    drug.dur_safety?.length && { id: "dur-safety", label: "DUR 안전성" },
    drug.deposit_method_qesitm && { id: "storage", label: "보관방법" },
  ].filter(Boolean) as TocItem[];

  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
      />
      {faqJsonLd && (
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{ __html: JSON.stringify(faqJsonLd) }}
        />
      )}

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
                  className="rounded-xl object-contain bg-white border border-gray-200 shadow-sm shrink-0"
                />
              )}
              <div className="min-w-0">
                <h1 className="text-2xl font-bold text-[var(--color-primary)] mb-2 break-keep">{drug.item_name}</h1>
                <div className="flex flex-wrap gap-2 text-sm mb-3">
                  {drug.entp_name && (
                    <span className="px-2 py-0.5 rounded-md bg-gray-100 text-gray-600">{drug.entp_name}</span>
                  )}
                  {otcLabel && (
                    <span className="px-2 py-0.5 rounded-md bg-blue-50 text-blue-700">{otcLabel}</span>
                  )}
                  {drug.class_no && (
                    <span className="px-2 py-0.5 rounded-md bg-gray-100 text-gray-500">분류 {drug.class_no}</span>
                  )}
                </div>
                <DataSource source="식약처 의약품안전나라" />
              </div>
            </div>

            {/* 정보 섹션 */}
            <div className="bg-white rounded-xl border border-gray-200 px-6 divide-y divide-gray-100 shadow-sm">
              <InfoSection id="efficacy" title="효능·효과" content={drug.efcy_qesitm} />
              {drug.use_method_qesitm ? (
                <DosageGuide id="usage" content={drug.use_method_qesitm} />
              ) : null}

              {drug.ingredients && drug.ingredients.length > 0 && (
                <div id="ingredients" className="scroll-mt-24">
                  <IngredientsTable ingredients={drug.ingredients} />
                </div>
              )}

              <InfoSection id="warnings" title="주의사항 (경고)" content={drug.atpn_warn_qesitm} />
              <InfoSection id="precautions" title="주의사항" content={drug.atpn_qesitm} />
              <InfoSection id="interactions" title="상호작용" content={drug.intrc_qesitm} />
              <FoodInteractionSection intrcText={drug.intrc_qesitm} />
              <InfoSection id="side-effects" title="부작용" content={drug.se_qesitm} />

              {drug.dur_safety && drug.dur_safety.length > 0 && (
                <DURSafetySection items={drug.dur_safety} />
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
                imageUrl={`${process.env.NEXT_PUBLIC_SITE_URL || "https://pillright.com"}/api/og?title=${encodeURIComponent(drug.item_name)}&type=drug`}
                pageUrl={`${process.env.NEXT_PUBLIC_SITE_URL || "https://pillright.com"}/drugs/${slug}`}
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
                      className="flex items-center gap-3 p-3 bg-white rounded-xl border border-gray-200 hover:border-[var(--color-primary-100)] hover:shadow-sm transition-all"
                    >
                      {rd.item_image ? (
                        <SafeImage
                          src={rd.item_image}
                          alt={rd.item_name}
                          width={40}
                          height={40}
                          className="rounded-lg object-contain bg-white border border-gray-100 shrink-0"
                        />
                      ) : (
                        <div className="w-10 h-10 rounded-lg bg-[var(--color-primary-50)] flex items-center justify-center shrink-0">
                          <svg className="w-5 h-5 text-[var(--color-primary)]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" />
                          </svg>
                        </div>
                      )}
                      <div className="min-w-0">
                        <p className="text-sm font-medium text-gray-900 truncate">{rd.item_name}</p>
                        {rd.entp_name && <p className="text-xs text-gray-500 truncate">{rd.entp_name}</p>}
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
                className="text-xs text-gray-500 hover:text-[var(--color-primary)] underline underline-offset-2 transition-colors"
              >
                전문가용 상세 정보 보기
              </Link>
            </div>

            {/* 면책조항 */}
            <p className="text-xs text-gray-400 text-center mt-2">
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
              <div className="bg-white rounded-xl border border-gray-200 p-4">
                <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">바로가기</p>
                <ul className="space-y-1.5">
                  <li>
                    <Link href="/check" className="text-sm text-gray-600 hover:text-[var(--color-primary)] transition-colors">
                      상호작용 체크
                    </Link>
                  </li>
                  <li>
                    <Link href="/drugs" className="text-sm text-gray-600 hover:text-[var(--color-primary)] transition-colors">
                      의약품 목록
                    </Link>
                  </li>
                  <li>
                    <Link href="/cabinet" className="text-sm text-gray-600 hover:text-[var(--color-primary)] transition-colors">
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
