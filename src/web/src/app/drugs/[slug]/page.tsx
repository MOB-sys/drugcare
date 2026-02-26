import type { Metadata } from "next";
import Image from "next/image";
import { notFound } from "next/navigation";
import { getDrugBySlug, getAllDrugSlugs } from "@/lib/api/drugs";
import { InfoSection } from "@/components/detail/InfoSection";
import { IngredientsTable } from "@/components/detail/IngredientsTable";
import { CheckCTA } from "@/components/detail/CheckCTA";
import { AdBanner } from "@/components/ads/AdBanner";

interface PageProps {
  params: Promise<{ slug: string }>;
}

/* ── SSG ────────────────────────────────────────── */

export async function generateStaticParams() {
  try {
    const slugs = await getAllDrugSlugs();
    return slugs.map((slug) => ({ slug }));
  } catch {
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
    const siteUrl = process.env.NEXT_PUBLIC_SITE_URL || "https://yakmeogeo.com";
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

  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
      />

      <article className="max-w-3xl mx-auto px-4 py-8">
        {/* 헤더 */}
        <div className="flex gap-6 mb-8">
          {drug.item_image && (
            <Image
              src={drug.item_image}
              alt={drug.item_name}
              width={128}
              height={128}
              priority
              sizes="128px"
              className="rounded-lg object-contain bg-white border border-gray-200 shrink-0"
            />
          )}
          <div className="min-w-0">
            <h1 className="text-2xl font-bold text-gray-900 mb-2 break-keep">{drug.item_name}</h1>
            <div className="flex flex-wrap gap-2 text-sm">
              {drug.entp_name && (
                <span className="px-2 py-0.5 rounded bg-gray-100 text-gray-600">{drug.entp_name}</span>
              )}
              {otcLabel && (
                <span className="px-2 py-0.5 rounded bg-blue-50 text-blue-700">{otcLabel}</span>
              )}
              {drug.class_no && (
                <span className="px-2 py-0.5 rounded bg-gray-100 text-gray-500">분류 {drug.class_no}</span>
              )}
            </div>
          </div>
        </div>

        {/* 정보 섹션 */}
        <div className="bg-white rounded-xl border border-gray-200 px-6 divide-y divide-gray-100">
          <InfoSection title="효능·효과" content={drug.efcy_qesitm} />
          <InfoSection title="용법·용량" content={drug.use_method_qesitm} />

          {drug.ingredients && drug.ingredients.length > 0 && (
            <IngredientsTable ingredients={drug.ingredients} />
          )}

          <InfoSection title="주의사항 (경고)" content={drug.atpn_warn_qesitm} />
          <InfoSection title="주의사항" content={drug.atpn_qesitm} />
          <InfoSection title="상호작용" content={drug.intrc_qesitm} />
          <InfoSection title="부작용" content={drug.se_qesitm} />
          <InfoSection title="보관방법" content={drug.deposit_method_qesitm} />
        </div>

        {/* CTA */}
        <CheckCTA itemType="drug" itemId={drug.id} itemName={drug.item_name} />

        {/* 광고 */}
        <AdBanner slot="drug-detail-bottom" format="horizontal" />

        {/* 면책조항 */}
        <p className="text-xs text-gray-400 text-center mt-4">
          이 정보는 식약처 공공데이터를 기반으로 하며, 의사/약사의 전문적 판단을 대체하지 않습니다.
        </p>
      </article>
    </>
  );
}
