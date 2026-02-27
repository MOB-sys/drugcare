import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { getTipBySlug, getAllTipSlugs } from "@/lib/data/tips";
import { AdBanner } from "@/components/ads/AdBanner";
import { Breadcrumbs } from "@/components/common/Breadcrumbs";

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

  const siteUrl = process.env.NEXT_PUBLIC_SITE_URL || "https://pillright.com";
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
    author: { "@type": "Organization", name: "PillRight" },
    publisher: { "@type": "Organization", name: "PillRight" },
    keywords: tip.tags.join(", "),
  };

  /** 마크다운 텍스트를 간단히 HTML로 변환 */
  const contentHtml = tip.content
    .replace(/^## (.+)$/gm, '<h2 class="text-xl font-bold text-[var(--color-primary)] mt-8 mb-3">$1</h2>')
    .replace(/^### (.+)$/gm, '<h3 class="text-lg font-semibold text-gray-800 mt-6 mb-2">$1</h3>')
    .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
    .replace(/^> (.+)$/gm, '<blockquote class="border-l-4 border-[var(--color-primary-100)] pl-4 text-sm text-gray-500 italic my-4">$1</blockquote>')
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
        <p className="text-gray-500 mb-6">{tip.description}</p>

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
        <div
          className="prose prose-gray max-w-none"
          dangerouslySetInnerHTML={{ __html: contentHtml }}
        />

        {/* 광고 */}
        <AdBanner slot="tip-detail-bottom" format="auto" />

        {/* CTA */}
        <div className="mt-8 bg-[var(--color-primary-50)] border border-[var(--color-primary-100)] rounded-xl p-6 text-center">
          <p className="text-lg font-semibold text-gray-900 mb-2">
            지금 복용 중인 약, 괜찮은지 확인해보세요
          </p>
          <p className="text-sm text-gray-500 mb-4">
            PillRight에서 3초 만에 상호작용을 체크할 수 있습니다.
          </p>
          <Link
            href="/check"
            className="inline-block px-6 py-3 rounded-xl text-white font-semibold bg-[var(--color-primary)] hover:bg-[var(--color-primary-dark)] shadow-md transition-all"
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
