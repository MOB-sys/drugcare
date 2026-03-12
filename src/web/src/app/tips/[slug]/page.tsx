import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { getTipBySlug, getAllTipSlugs } from "@/lib/content/loader";
import { AdBanner } from "@/components/ads/AdBanner";
import { Breadcrumbs } from "@/components/common/Breadcrumbs";
import { MarkdownRenderer } from "@/components/content/MarkdownRenderer";
import { SITE_URL } from "@/lib/constants/site";

interface PageProps {
  params: Promise<{ slug: string }>;
}

/* ── SSG ────────────────────────────────────────── */

export function generateStaticParams() {
  return getAllTipSlugs().map((slug) => ({ slug }));
}

export async function generateMetadata({ params }: PageProps): Promise<Metadata> {
  const { slug } = await params;
  const tip = getTipBySlug(slug);
  if (!tip) return { title: "건강팁" };

  const siteUrl = SITE_URL;
  return {
    title: tip.title,
    description: tip.description,
    keywords: tip.tags,
    alternates: { canonical: `/tips/${slug}` },
    openGraph: {
      title: tip.title,
      description: tip.description,
      type: "article",
      images: [
        {
          url: `${siteUrl}/api/og?title=${encodeURIComponent(tip.title)}&type=tip`,
          width: 1200,
          height: 630,
          alt: tip.title,
        },
      ],
    },
  };
}

/* ── Page ───────────────────────────────────────── */

export default async function TipDetailPage({ params }: PageProps) {
  const { slug } = await params;
  const tip = getTipBySlug(slug);
  if (!tip) notFound();

  const jsonLd = {
    "@context": "https://schema.org",
    "@type": "Article",
    headline: tip.title,
    description: tip.description,
    author: { "@type": "Organization", name: "약잘알" },
    publisher: { "@type": "Organization", name: "약잘알" },
    keywords: tip.tags.join(", "),
  };

  /* Markdown 렌더링은 공통 컴포넌트에 위임 */

  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd).replace(/</g, '\\u003c') }}
      />

      <Breadcrumbs
        items={[
          { label: "홈", href: "/" },
          { label: "건강팁", href: "/tips" },
          { label: tip.title },
        ]}
      />

      <article className="max-w-3xl mx-auto px-4 py-6">
        <h1 className="text-2xl font-bold text-[var(--color-primary)] mb-3 break-keep">
          {tip.title}
        </h1>
        <p className="text-gray-500 dark:text-gray-400 mb-6">{tip.description}</p>

        <div className="flex flex-wrap gap-1.5 mb-8">
          {tip.tags.map((tag) => (
            <span
              key={tag}
              className="text-xs px-2 py-0.5 rounded-full bg-[var(--color-primary-50)] text-[var(--color-primary)]"
            >
              {tag}
            </span>
          ))}
        </div>

        {/* 본문 */}
        <MarkdownRenderer content={tip.content} />

        {/* 광고 */}
        <AdBanner slot="tip-detail-bottom" format="auto" />

        {/* CTA */}
        <div className="mt-8 bg-[var(--color-primary-50)] border border-[var(--color-primary-100)] rounded-xl p-6 text-center">
          <p className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
            지금 복용 중인 약, 괜찮은지 확인해보세요
          </p>
          <p className="text-sm text-gray-500 dark:text-gray-400 mb-4">
            약잘알에서 3초 만에 상호작용을 체크할 수 있습니다.
          </p>
          <Link
            href="/check"
            className="inline-block px-6 py-3 rounded-xl text-white font-semibold bg-[var(--color-primary)] hover:bg-[var(--color-primary-dark)] shadow-md transition-all"
          >
            상호작용 체크하러 가기
          </Link>
        </div>

        {/* 면책조항 */}
        <p className="text-xs text-gray-400 dark:text-gray-500 text-center mt-6">
          이 정보는 일반적인 건강 정보이며, 의사/약사의 전문적 판단을 대체하지 않습니다.
        </p>
      </article>
    </>
  );
}
