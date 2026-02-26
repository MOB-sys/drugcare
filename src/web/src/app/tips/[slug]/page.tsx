import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { tips, getTipBySlug, getAllTipSlugs } from "@/lib/data/tips";
import { AdBanner } from "@/components/ads/AdBanner";

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

  const siteUrl = process.env.NEXT_PUBLIC_SITE_URL || "https://yakmeogeo.com";
  return {
    title: tip.title,
    description: tip.description,
    keywords: tip.tags,
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
    author: { "@type": "Organization", name: "약먹어" },
    publisher: { "@type": "Organization", name: "약먹어" },
    keywords: tip.tags.join(", "),
  };

  /** 마크다운 텍스트를 간단히 HTML로 변환 */
  const contentHtml = tip.content
    .replace(/^## (.+)$/gm, '<h2 class="text-xl font-bold text-gray-900 mt-8 mb-3">$1</h2>')
    .replace(/^### (.+)$/gm, '<h3 class="text-lg font-semibold text-gray-800 mt-6 mb-2">$1</h3>')
    .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
    .replace(/^> (.+)$/gm, '<blockquote class="border-l-4 border-gray-300 pl-4 text-sm text-gray-500 italic my-4">$1</blockquote>')
    .replace(/^---$/gm, '<hr class="my-6 border-gray-200" />')
    .replace(/\n\n/g, '</p><p class="text-gray-700 leading-relaxed mb-3">')
    .replace(/^(?!<)/, '<p class="text-gray-700 leading-relaxed mb-3">')
    .concat("</p>");

  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
      />

      <article className="max-w-3xl mx-auto px-4 py-8">
        <h1 className="text-2xl font-bold text-gray-900 mb-3 break-keep">
          {tip.title}
        </h1>
        <p className="text-gray-500 mb-6">{tip.description}</p>

        <div className="flex flex-wrap gap-1.5 mb-8">
          {tip.tags.map((tag) => (
            <span
              key={tag}
              className="text-xs px-2 py-0.5 rounded-full bg-gray-100 text-gray-500"
            >
              {tag}
            </span>
          ))}
        </div>

        {/* 본문 */}
        <div
          className="prose prose-gray max-w-none"
          dangerouslySetInnerHTML={{ __html: contentHtml }}
        />

        {/* 광고 */}
        <AdBanner slot="tip-detail-bottom" format="auto" />

        {/* CTA */}
        <div className="mt-8 bg-[var(--color-brand)] bg-opacity-5 border border-[var(--color-brand)] rounded-xl p-6 text-center">
          <p className="text-lg font-semibold text-gray-900 mb-2">
            지금 복용 중인 약, 괜찮은지 확인해보세요
          </p>
          <p className="text-sm text-gray-500 mb-4">
            약먹어에서 3초 만에 상호작용을 체크할 수 있습니다.
          </p>
          <Link
            href="/check"
            className="inline-block px-6 py-3 rounded-lg text-white font-semibold bg-[var(--color-brand)] hover:bg-[var(--color-brand-dark)] transition-colors"
          >
            상호작용 체크하러 가기
          </Link>
        </div>

        {/* 면책조항 */}
        <p className="text-xs text-gray-400 text-center mt-6">
          이 정보는 일반적인 건강 정보이며, 의사/약사의 전문적 판단을 대체하지 않습니다.
        </p>
      </article>
    </>
  );
}
