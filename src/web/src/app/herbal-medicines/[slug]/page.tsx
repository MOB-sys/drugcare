import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { getHerbalMedicineBySlug } from "@/lib/api/herbal";
import { InfoSection } from "@/components/detail/InfoSection";
import { CheckCTA } from "@/components/detail/CheckCTA";
import { AddToCabinetButton } from "@/components/detail/AddToCabinetButton";
import { AdBanner } from "@/components/ads/AdBanner";
import { Breadcrumbs } from "@/components/common/Breadcrumbs";
import { DataSource } from "@/components/common/DataSource";
import { KakaoShareButton } from "@/components/common/KakaoShareButton";
import { SITE_URL } from "@/lib/constants/site";

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
    const herbal = await getHerbalMedicineBySlug(slug);
    const displayName = herbal.korean_name ?? herbal.name;
    const title = `${displayName} 효능·성질·주의사항`;
    const description = herbal.efficacy
      ? `${displayName} — ${herbal.efficacy.slice(0, 120)}`
      : `${displayName} 한약재 상세 정보를 확인하세요.`;
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
            url: `${siteUrl}/api/og?title=${encodeURIComponent(displayName)}&type=herbal`,
            width: 1200,
            height: 630,
            alt: title,
          },
        ],
      },
      twitter: { card: "summary_large_image", title, description },
      alternates: { canonical: `/herbal-medicines/${slug}` },
    };
  } catch {
    return { title: "한약재 정보" };
  }
}

/** 성질(properties) 정보를 표시. */
function renderProperties(properties: Record<string, unknown> | null) {
  if (!properties || Object.keys(properties).length === 0) return null;
  const entries = Object.entries(properties).filter(([, v]) => v != null && v !== "");
  if (entries.length === 0) return null;

  const LABEL_MAP: Record<string, string> = {
    nature: "성질(性)",
    flavor: "맛(味)",
    meridian: "귀경(歸經)",
    toxicity: "독성",
  };

  return (
    <div id="properties" className="py-5 scroll-mt-24">
      <h2 className="text-base font-semibold text-gray-900 dark:text-gray-100 mb-3">성질·귀경</h2>
      <dl className="grid grid-cols-[auto_1fr] gap-x-4 gap-y-2 text-sm">
        {entries.map(([key, val]) => (
          <div key={key} className="contents">
            <dt className="text-gray-500 dark:text-gray-400 font-medium">{LABEL_MAP[key] ?? key}</dt>
            <dd className="text-gray-900 dark:text-gray-100">{String(val)}</dd>
          </div>
        ))}
      </dl>
    </div>
  );
}

/* ── Page ───────────────────────────────────────── */

export default async function HerbalMedicineDetailPage({ params }: PageProps) {
  const { slug } = await params;
  let herbal;
  try {
    herbal = await getHerbalMedicineBySlug(slug);
  } catch {
    notFound();
  }

  const displayName = herbal.korean_name ?? herbal.name;

  const jsonLd = {
    "@context": "https://schema.org",
    "@type": "Article",
    name: displayName,
    description: herbal.efficacy ?? herbal.description ?? undefined,
    about: {
      "@type": "Drug",
      name: displayName,
      alternateName: herbal.latin_name ?? undefined,
      category: herbal.category ?? "한약재",
    },
  };

  const faqEntries: { question: string; answer: string }[] = [];
  if (herbal.efficacy) faqEntries.push({ question: `${displayName}의 효능은?`, answer: herbal.efficacy });
  if (herbal.description) faqEntries.push({ question: `${displayName}이란?`, answer: herbal.description });
  if (herbal.precautions) faqEntries.push({ question: `${displayName} 복용 시 주의사항은?`, answer: herbal.precautions });

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

      <Breadcrumbs
        items={[
          { label: "홈", href: "/" },
          { label: "한약재", href: "/herbal-medicines" },
          { label: displayName },
        ]}
      />

      <div className="max-w-5xl mx-auto px-4 py-6">
        <article className="max-w-3xl">
          {/* 헤더 */}
          <div className="mb-6">
            <h1 className="text-2xl font-bold text-[var(--color-primary)] mb-2 break-keep">{displayName}</h1>
            <div className="flex flex-wrap gap-2 text-sm mb-3">
              {herbal.name !== displayName && (
                <span className="px-2 py-0.5 rounded-md bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300">
                  {herbal.name}
                </span>
              )}
              {herbal.latin_name && (
                <span className="px-2 py-0.5 rounded-md bg-gray-100 dark:bg-gray-700 text-gray-500 dark:text-gray-400 italic">
                  {herbal.latin_name}
                </span>
              )}
              {herbal.category && (
                <span className="px-2 py-0.5 rounded-md bg-purple-50 dark:bg-purple-900/30 text-purple-700 dark:text-purple-300">
                  {herbal.category}
                </span>
              )}
            </div>
            <DataSource source="식약처 생약정보" />
          </div>

          {/* 정보 섹션 */}
          <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 px-6 divide-y divide-gray-100 dark:divide-gray-700 shadow-sm">
            <InfoSection id="description" title="설명" content={herbal.description} />
            {renderProperties(herbal.properties)}
            <InfoSection id="efficacy" title="효능" content={herbal.efficacy} />
            <InfoSection id="precautions" title="주의사항" content={herbal.precautions} />
          </div>

          {/* CTA */}
          <CheckCTA itemType="herbal" itemId={herbal.id} itemName={displayName} />
          <div className="pb-4 flex flex-wrap items-center gap-3">
            <AddToCabinetButton itemType="herbal" itemId={herbal.id} itemName={displayName} />
            <KakaoShareButton
              title={`${displayName} 효능·성질·주의사항`}
              description={herbal.efficacy ? herbal.efficacy.slice(0, 100) : `${displayName} 한약재 상세 정보를 확인하세요.`}
              imageUrl={`${SITE_URL}/api/og?title=${encodeURIComponent(displayName)}&type=herbal`}
              pageUrl={`${SITE_URL}/herbal-medicines/${slug}`}
            />
          </div>

          {/* 광고 */}
          <AdBanner slot="herbal-detail-bottom" format="horizontal" />

          {/* 면책조항 */}
          <p className="text-xs text-gray-400 dark:text-gray-500 text-center mt-4">
            이 정보는 식약처 공공데이터를 기반으로 하며, 의사/약사의 전문적 판단을 대체하지 않습니다.
          </p>
        </article>
      </div>
    </>
  );
}
