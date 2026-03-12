import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { getResearchBySlug, getAllResearchSlugs } from "@/lib/content/loader";
import { AdBanner } from "@/components/ads/AdBanner";
import { Breadcrumbs } from "@/components/common/Breadcrumbs";
import { MarkdownRenderer } from "@/components/content/MarkdownRenderer";
import { SITE_URL } from "@/lib/constants/site";

interface PageProps {
  params: Promise<{ slug: string }>;
}

export function generateStaticParams() {
  return getAllResearchSlugs().map((slug) => ({ slug }));
}

export async function generateMetadata({ params }: PageProps): Promise<Metadata> {
  const { slug } = await params;
  const item = getResearchBySlug(slug);
  if (!item) return { title: "연구 요약" };

  return {
    title: `${item.title} | 약잘알`,
    description: item.description,
    keywords: item.tags,
    alternates: { canonical: `/research/${slug}` },
    openGraph: {
      title: item.title,
      description: item.description,
      type: "article",
      images: [{
        url: `${SITE_URL}/api/og?title=${encodeURIComponent(item.title)}&type=research`,
        width: 1200, height: 630, alt: item.title,
      }],
    },
  };
}

const EVIDENCE_BADGE: Record<string, string> = {
  high: "bg-green-50 dark:bg-green-900/30 text-green-700 dark:text-green-400",
  moderate: "bg-amber-50 dark:bg-amber-900/30 text-amber-700 dark:text-amber-400",
  low: "bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300",
};

const EVIDENCE_LABELS: Record<string, string> = {
  high: "높은 근거 수준", moderate: "보통 근거 수준", low: "낮은 근거 수준",
};

export default async function ResearchDetailPage({ params }: PageProps) {
  const { slug } = await params;
  const item = getResearchBySlug(slug);
  if (!item) notFound();

  const jsonLd = {
    "@context": "https://schema.org",
    "@type": "ScholarlyArticle",
    headline: item.title,
    description: item.description,
    datePublished: item.publishedAt,
    author: item.authors?.map((name) => ({ "@type": "Person", name })),
    publisher: { "@type": "Organization", name: "약잘알 (PillRight)", url: SITE_URL },
  };

  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd).replace(/</g, "\\u003c") }}
      />

      <Breadcrumbs
        items={[
          { label: "홈", href: "/" },
          { label: "최신 연구", href: "/research" },
          { label: item.title },
        ]}
      />

      <article className="max-w-3xl mx-auto px-4 py-6">
        <h1 className="text-2xl font-bold text-[var(--color-primary)] mb-3 break-keep">
          {item.title}
        </h1>

        {/* 메타 정보 */}
        <div className="flex flex-wrap items-center gap-2 text-sm mb-4">
          {item.journal && (
            <span className="text-gray-500 dark:text-gray-400 italic">{item.journal}</span>
          )}
          {item.authors && item.authors.length > 0 && (
            <span className="text-gray-400 dark:text-gray-500">· {item.authors.join(", ")}</span>
          )}
        </div>

        <div className="flex flex-wrap gap-2 mb-6">
          {item.evidenceLevel && (
            <span className={`text-xs px-2.5 py-1 rounded-full font-medium ${EVIDENCE_BADGE[item.evidenceLevel] ?? EVIDENCE_BADGE.low}`}>
              {EVIDENCE_LABELS[item.evidenceLevel] ?? item.evidenceLevel}
            </span>
          )}
          {item.pubmedId && (
            <a
              href={`https://pubmed.ncbi.nlm.nih.gov/${item.pubmedId}/`}
              target="_blank"
              rel="noopener noreferrer"
              className="text-xs px-2.5 py-1 rounded-full bg-blue-50 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 hover:underline"
            >
              PubMed: {item.pubmedId}
            </a>
          )}
          {item.doi && (
            <a
              href={`https://doi.org/${item.doi}`}
              target="_blank"
              rel="noopener noreferrer"
              className="text-xs px-2.5 py-1 rounded-full bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300 hover:underline"
            >
              DOI
            </a>
          )}
          <span className="text-xs text-gray-400 dark:text-gray-500 py-1">{item.publishedAt}</span>
        </div>

        <div className="flex flex-wrap gap-1.5 mb-8">
          {item.tags.map((tag) => (
            <span key={tag} className="text-xs px-2 py-0.5 rounded-full bg-[var(--color-primary-50)] text-[var(--color-primary)]">
              {tag}
            </span>
          ))}
        </div>

        <MarkdownRenderer content={item.content} />

        <AdBanner slot="research-detail-bottom" format="auto" />

        <div className="mt-8 bg-[var(--color-primary-50)] border border-[var(--color-primary-100)] rounded-xl p-6 text-center">
          <p className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
            이 연구와 관련된 약물을 복용 중인가요?
          </p>
          <Link
            href="/check"
            className="inline-block px-6 py-3 rounded-xl text-white font-semibold bg-[var(--color-primary)] hover:bg-[var(--color-primary-dark)] shadow-md transition-all"
          >
            상호작용 체크하러 가기
          </Link>
        </div>

        <p className="text-xs text-gray-400 dark:text-gray-500 text-center mt-6">
          이 정보는 의학 논문의 요약이며, 의사/약사의 전문적 판단을 대체하지 않습니다.
        </p>
      </article>
    </>
  );
}
