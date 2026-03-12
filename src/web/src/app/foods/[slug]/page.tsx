import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { getFoodBySlug } from "@/lib/api/foods";
import { InfoSection } from "@/components/detail/InfoSection";
import { CheckCTA } from "@/components/detail/CheckCTA";
import { AddToCabinetButton } from "@/components/detail/AddToCabinetButton";
import { AdBanner } from "@/components/ads/AdBanner";
import { Breadcrumbs } from "@/components/common/Breadcrumbs";
import { DataSource } from "@/components/common/DataSource";
import { KakaoShareButton } from "@/components/common/KakaoShareButton";
import { SITE_URL } from "@/lib/constants/site";
import { DetailViewTracker } from "@/components/common/DetailViewTracker";

interface PageProps {
  params: Promise<{ slug: string }>;
}

/* ── ISR ────────────────────────────────────────── */

export const dynamicParams = true;
export const revalidate = 86400;

export async function generateStaticParams() {
  return [];
}

export async function generateMetadata({ params }: PageProps): Promise<Metadata> {
  const { slug } = await params;
  try {
    const food = await getFoodBySlug(slug);
    const title = `${food.name} 영양성분·상호작용 정보`;
    const description = food.description
      ? `${food.name} — ${food.description.slice(0, 120)}`
      : `${food.name} 식품 상세 정보를 확인하세요.`;
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
            url: `${siteUrl}/api/og?title=${encodeURIComponent(food.name)}&type=food`,
            width: 1200,
            height: 630,
            alt: title,
          },
        ],
      },
      twitter: { card: "summary_large_image", title, description },
      alternates: { canonical: `/foods/${slug}` },
    };
  } catch {
    return { title: "식품 정보" };
  }
}

/** 영양소 데이터를 테이블 행으로 변환. */
function renderNutrients(nutrients: Record<string, unknown>[] | null) {
  if (!nutrients || nutrients.length === 0) return null;

  // 데이터 구조에 따라 컬럼 결정: amount가 있으면 함량 표시, note만 있으면 설명 표시
  const hasAmount = nutrients.some((n) => n.amount != null);

  return (
    <div id="nutrients" className="py-5 scroll-mt-24">
      <h2 className="text-base font-semibold text-gray-900 dark:text-gray-100 mb-3">영양성분</h2>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-gray-200 dark:border-gray-700">
              <th className="text-left py-2 pr-4 text-gray-500 dark:text-gray-400 font-medium">성분명</th>
              <th className="text-right py-2 text-gray-500 dark:text-gray-400 font-medium">
                {hasAmount ? "함량" : "특성"}
              </th>
            </tr>
          </thead>
          <tbody>
            {nutrients.map((n, i) => {
              const name = String(n.name ?? n.nutrient_name ?? "");
              const value = hasAmount
                ? (n.amount != null ? `${n.amount}${n.unit ? ` ${n.unit}` : ""}` : "-")
                : String(n.note ?? n.description ?? n.effect ?? "-");
              return (
                <tr key={i} className="border-b border-gray-100 dark:border-gray-700/50">
                  <td className="py-2 pr-4 text-gray-900 dark:text-gray-100">{name}</td>
                  <td className="py-2 text-right text-gray-600 dark:text-gray-300">{value}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}

/* ── Page ───────────────────────────────────────── */

export default async function FoodDetailPage({ params }: PageProps) {
  const { slug } = await params;
  let food;
  try {
    food = await getFoodBySlug(slug);
  } catch {
    notFound();
  }

  const jsonLd = {
    "@context": "https://schema.org",
    "@type": "Article",
    name: food.name,
    description: food.description ?? undefined,
    about: {
      "@type": "Thing",
      name: food.name,
      additionalType: "Food",
    },
  };

  const faqEntries: { question: string; answer: string }[] = [];
  if (food.description) faqEntries.push({ question: `${food.name}이란?`, answer: food.description });
  if (food.common_names?.length) faqEntries.push({ question: `${food.name}의 다른 이름은?`, answer: food.common_names.join(", ") });

  const faqJsonLd = faqEntries.length > 0 ? {
    "@context": "https://schema.org",
    "@type": "FAQPage",
    mainEntity: faqEntries.map((e) => ({
      "@type": "Question",
      name: e.question,
      acceptedAnswer: { "@type": "Answer", text: e.answer },
    })),
  } : null;

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

      <DetailViewTracker type="food" id={food.id} name={food.name} />

      <Breadcrumbs
        items={[
          { label: "홈", href: "/" },
          { label: "식품", href: "/foods" },
          { label: food.name },
        ]}
      />

      <div className="max-w-5xl mx-auto px-4 py-6">
        <article className="max-w-3xl">
          {/* 헤더 */}
          <div className="mb-6">
            <h1 className="text-2xl font-bold text-[var(--color-primary)] mb-2 break-keep">{food.name}</h1>
            <div className="flex flex-wrap gap-2 text-sm mb-3">
              {food.category && (
                <span className="px-2 py-0.5 rounded-md bg-orange-50 dark:bg-orange-900/30 text-orange-700 dark:text-orange-300">
                  {food.category}
                </span>
              )}
              {food.common_names && food.common_names.length > 0 && (
                <span className="px-2 py-0.5 rounded-md bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300">
                  {food.common_names.join(", ")}
                </span>
              )}
            </div>
            <DataSource source="식약처 식품안전정보" />
          </div>

          {/* 정보 섹션 */}
          <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 px-6 divide-y divide-gray-100 dark:divide-gray-700 shadow-sm">
            <InfoSection id="description" title="설명" content={food.description} />
            {renderNutrients(food.nutrients)}
          </div>

          {/* CTA */}
          <CheckCTA itemType="food" itemId={food.id} itemName={food.name} />
          <div className="pb-4 flex flex-wrap items-center gap-3">
            <AddToCabinetButton itemType="food" itemId={food.id} itemName={food.name} />
            <KakaoShareButton
              title={`${food.name} 영양성분·상호작용 정보`}
              description={food.description ? food.description.slice(0, 100) : `${food.name} 식품 상세 정보를 확인하세요.`}
              imageUrl={`${SITE_URL}/api/og?title=${encodeURIComponent(food.name)}&type=food`}
              pageUrl={`${SITE_URL}/foods/${slug}`}
            />
          </div>

          {/* 광고 */}
          <AdBanner slot="food-detail-bottom" format="horizontal" />

          {/* 면책조항 */}
          <p className="text-xs text-gray-400 dark:text-gray-500 text-center mt-4">
            이 정보는 식약처 공공데이터를 기반으로 하며, 의사/약사의 전문적 판단을 대체하지 않습니다.
          </p>
        </article>
      </div>
    </>
  );
}
