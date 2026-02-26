import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { getSupplementBySlug, getAllSupplementSlugs } from "@/lib/api/supplements";
import { InfoSection } from "@/components/detail/InfoSection";
import { IngredientsTable } from "@/components/detail/IngredientsTable";
import { CheckCTA } from "@/components/detail/CheckCTA";
import { AddToCabinetButton } from "@/components/detail/AddToCabinetButton";
import { AdBanner } from "@/components/ads/AdBanner";
import type { IngredientInfo } from "@/types/drug";

interface PageProps {
  params: Promise<{ slug: string }>;
}

/* ── SSG ────────────────────────────────────────── */

export async function generateStaticParams() {
  try {
    const slugs = await getAllSupplementSlugs();
    return slugs.map((slug) => ({ slug }));
  } catch {
    return [];
  }
}

export async function generateMetadata({ params }: PageProps): Promise<Metadata> {
  const { slug } = await params;
  try {
    const supp = await getSupplementBySlug(slug);
    const title = `${supp.product_name} 기능성·성분·섭취방법`;
    const description = supp.functionality
      ? `${supp.product_name} — ${supp.functionality.slice(0, 120)}`
      : `${supp.product_name} 건강기능식품 상세 정보를 확인하세요.`;
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
            url: `${siteUrl}/api/og?title=${encodeURIComponent(supp.product_name)}&type=supplement`,
            width: 1200,
            height: 630,
            alt: title,
          },
        ],
      },
    };
  } catch {
    return { title: "영양제 정보" };
  }
}

/** JSONB 성분 데이터를 IngredientInfo[]로 정규화. */
function normalizeIngredients(raw: Record<string, unknown>[] | null): IngredientInfo[] {
  if (!raw) return [];
  return raw.map((item) => ({
    name: String(item.name ?? item.ingredient_name ?? ""),
    amount: item.amount != null ? String(item.amount) : null,
    unit: item.unit != null ? String(item.unit) : null,
  }));
}

/* ── Page ───────────────────────────────────────── */

export default async function SupplementDetailPage({ params }: PageProps) {
  const { slug } = await params;
  let supp;
  try {
    supp = await getSupplementBySlug(slug);
  } catch {
    notFound();
  }

  const ingredients = normalizeIngredients(supp.ingredients);

  const jsonLd = {
    "@context": "https://schema.org",
    "@type": "Product",
    name: supp.product_name,
    manufacturer: supp.company ? { "@type": "Organization", name: supp.company } : undefined,
    description: supp.functionality ?? undefined,
    category: supp.category ?? "건강기능식품",
  };

  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
      />

      <article className="max-w-3xl mx-auto px-4 py-8">
        {/* 헤더 */}
        <div className="mb-8">
          <h1 className="text-2xl font-bold text-[var(--color-primary)] mb-2 break-keep">{supp.product_name}</h1>
          <div className="flex flex-wrap gap-2 text-sm">
            {supp.company && (
              <span className="px-2 py-0.5 rounded-md bg-gray-100 text-gray-600">{supp.company}</span>
            )}
            {supp.category && (
              <span className="px-2 py-0.5 rounded-md bg-emerald-50 text-emerald-700">{supp.category}</span>
            )}
            {supp.registration_no && (
              <span className="px-2 py-0.5 rounded-md bg-gray-100 text-gray-500">{supp.registration_no}</span>
            )}
          </div>
        </div>

        {/* 정보 섹션 */}
        <div className="bg-white rounded-xl border border-gray-200 px-6 divide-y divide-gray-100 shadow-sm">
          <InfoSection title="기능성" content={supp.functionality} />
          <InfoSection title="주성분" content={supp.main_ingredient} />

          {ingredients.length > 0 && <IngredientsTable ingredients={ingredients} />}

          <InfoSection title="섭취방법" content={supp.intake_method} />
          <InfoSection title="섭취 시 주의사항" content={supp.precautions} />
        </div>

        {/* CTA */}
        <CheckCTA itemType="supplement" itemId={supp.id} itemName={supp.product_name} />
        <div className="pb-4">
          <AddToCabinetButton itemType="supplement" itemId={supp.id} itemName={supp.product_name} />
        </div>

        {/* 광고 */}
        <AdBanner slot="supplement-detail-bottom" format="horizontal" />

        {/* 면책조항 */}
        <p className="text-xs text-gray-400 text-center mt-4">
          이 정보는 식약처 공공데이터를 기반으로 하며, 의사/약사의 전문적 판단을 대체하지 않습니다.
        </p>
      </article>
    </>
  );
}
