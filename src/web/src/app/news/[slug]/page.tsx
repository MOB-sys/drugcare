import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { getNewsBySlug, getAllNewsSlugs } from "@/lib/content/loader";
import { AdBanner } from "@/components/ads/AdBanner";
import { Breadcrumbs } from "@/components/common/Breadcrumbs";
import { MarkdownRenderer } from "@/components/content/MarkdownRenderer";
import { SITE_URL } from "@/lib/constants/site";

interface PageProps {
  params: Promise<{ slug: string }>;
}

export function generateStaticParams() {
  return getAllNewsSlugs().map((slug) => ({ slug }));
}

export async function generateMetadata({ params }: PageProps): Promise<Metadata> {
  const { slug } = await params;
  const news = getNewsBySlug(slug);
  if (!news) return { title: "의약품 소식" };

  return {
    title: `${news.title} | 약잘알`,
    description: news.description,
    keywords: news.tags,
    alternates: { canonical: `/news/${slug}` },
    openGraph: {
      title: news.title,
      description: news.description,
      type: "article",
      images: [{
        url: `${SITE_URL}/api/og?title=${encodeURIComponent(news.title)}&type=news`,
        width: 1200, height: 630, alt: news.title,
      }],
    },
  };
}

const SEVERITY_STYLES = {
  danger: "bg-red-50 dark:bg-red-950/30 text-red-700 dark:text-red-400 border-red-200 dark:border-red-800",
  warning: "bg-amber-50 dark:bg-amber-950/30 text-amber-700 dark:text-amber-400 border-amber-200 dark:border-amber-800",
  info: "bg-blue-50 dark:bg-blue-950/30 text-blue-700 dark:text-blue-400 border-blue-200 dark:border-blue-800",
};

const SEVERITY_LABELS = { danger: "위험", warning: "주의", info: "정보" };
const SOURCE_LABELS: Record<string, string> = { mfds: "식약처", fda: "FDA", ema: "EMA" };

export default async function NewsDetailPage({ params }: PageProps) {
  const { slug } = await params;
  const news = getNewsBySlug(slug);
  if (!news) notFound();

  const severity = news.severity ?? "info";
  const jsonLd = {
    "@context": "https://schema.org",
    "@type": "NewsArticle",
    headline: news.title,
    description: news.description,
    datePublished: news.publishedAt,
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
          { label: "의약품 소식", href: "/news" },
          { label: news.title },
        ]}
      />

      <article className="max-w-3xl mx-auto px-4 py-6">
        {/* 심각도 배지 */}
        <div className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-lg border text-sm font-medium mb-4 ${SEVERITY_STYLES[severity]}`}>
          {SEVERITY_LABELS[severity]}
          {news.source && <span className="opacity-70">· {SOURCE_LABELS[news.source] ?? news.source}</span>}
        </div>

        <h1 className="text-2xl font-bold text-[var(--color-primary)] mb-3 break-keep">
          {news.title}
        </h1>
        <p className="text-gray-500 dark:text-gray-400 mb-2">{news.description}</p>
        <p className="text-xs text-gray-400 dark:text-gray-500 mb-6">{news.publishedAt}</p>

        <div className="flex flex-wrap gap-1.5 mb-8">
          {news.tags.map((tag) => (
            <span key={tag} className="text-xs px-2 py-0.5 rounded-full bg-[var(--color-primary-50)] text-[var(--color-primary)]">
              {tag}
            </span>
          ))}
        </div>

        <MarkdownRenderer content={news.content} />

        <AdBanner slot="news-detail-bottom" format="auto" />

        <div className="mt-8 bg-[var(--color-primary-50)] border border-[var(--color-primary-100)] rounded-xl p-6 text-center">
          <p className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
            복용 중인 약이 해당되는지 확인하세요
          </p>
          <Link
            href="/check"
            className="inline-block px-6 py-3 rounded-xl text-white font-semibold bg-[var(--color-primary)] hover:bg-[var(--color-primary-dark)] shadow-md transition-all"
          >
            상호작용 체크하러 가기
          </Link>
        </div>

        <p className="text-xs text-gray-400 dark:text-gray-500 text-center mt-6">
          이 정보는 공식 안전 정보를 기반으로 하며, 의사/약사의 전문적 판단을 대체하지 않습니다.
        </p>
      </article>
    </>
  );
}
