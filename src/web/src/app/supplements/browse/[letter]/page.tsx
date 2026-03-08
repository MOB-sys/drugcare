import type { Metadata } from "next";
import Link from "next/link";
import { searchSupplements } from "@/lib/api/supplements";
import { Breadcrumbs } from "@/components/common/Breadcrumbs";
import { AdBanner } from "@/components/ads/AdBanner";
import { ALL_LETTERS, CHOSUNG, matchesLetterKey } from "@/lib/utils/korean";

export const revalidate = 86400; // 24시간 ISR

interface PageProps {
  params: Promise<{ letter: string }>;
}

export function generateStaticParams() {
  return ALL_LETTERS.map((letter) => ({ letter }));
}

export async function generateMetadata({ params }: PageProps): Promise<Metadata> {
  const { letter } = await params;
  const particle = (CHOSUNG as readonly string[]).includes(letter) ? "으로" : "로";
  const title = `${letter}${particle} 시작하는 건강기능식품 목록`;
  return {
    title,
    description: `${letter}${particle} 시작하는 건강기능식품을 찾아보세요. 기능성, 성분, 섭취방법 정보를 확인할 수 있습니다.`,
  };
}

export default async function SupplementBrowsePage({ params }: PageProps) {
  const { letter } = await params;
  const particle = (CHOSUNG as readonly string[]).includes(letter) ? "으로" : "로";

  interface SuppItem {
    id: number;
    product_name: string;
    slug: string;
    company: string | null;
  }

  let supplements: SuppItem[] = [];

  try {
    const res = await searchSupplements("", 1, 2000);
    supplements = res.items
      .filter((s) => matchesLetterKey(s.product_name, letter))
      .map((s) => ({ id: s.id, product_name: s.product_name, slug: s.slug, company: s.company }));
  } catch {
    /* API 미연결 시 빈 목록 */
  }

  return (
    <>
      <Breadcrumbs
        items={[
          { label: "홈", href: "/" },
          { label: "건강기능식품 목록", href: "/supplements" },
          { label: `${letter} 건강기능식품` },
        ]}
      />

      <section className="max-w-3xl mx-auto px-4 py-6">
        <h1 className="text-2xl font-bold text-[var(--color-primary)] mb-2">
          {letter}{particle} 시작하는 건강기능식품
        </h1>
        <p className="text-[var(--color-text-secondary)] mb-6">
          총 {supplements.length}개의 건강기능식품이 있습니다.
        </p>

        {/* 인덱스 네비게이션 */}
        <nav className="flex flex-wrap gap-1 mb-8" aria-label="가나다 인덱스">
          {ALL_LETTERS.map((l) => (
            <Link
              key={l}
              href={`/supplements/browse/${encodeURIComponent(l)}`}
              className={`w-8 h-8 flex items-center justify-center rounded-lg text-xs font-medium transition-colors ${
                l === letter
                  ? "bg-[var(--color-primary)] text-white"
                  : "bg-gray-100 text-gray-600 hover:bg-[var(--color-primary-50)]"
              }`}
            >
              {l}
            </Link>
          ))}
        </nav>

        {/* 건강기능식품 목록 */}
        {supplements.length > 0 ? (
          <ul className="grid gap-1 sm:grid-cols-2">
            {supplements.map((supp) => (
              <li key={supp.id}>
                <Link
                  href={`/supplements/${supp.slug}`}
                  className="block px-3 py-2 rounded-lg hover:bg-[var(--color-primary-50)] transition-colors"
                >
                  <span className="text-sm font-medium text-[var(--color-text)]">{supp.product_name}</span>
                  {supp.company && (
                    <span className="ml-2 text-xs text-[var(--color-text-muted)]">{supp.company}</span>
                  )}
                </Link>
              </li>
            ))}
          </ul>
        ) : (
          <div className="text-center py-16 text-[var(--color-text-muted)]">
            해당 글자로 시작하는 건강기능식품이 없습니다.
          </div>
        )}

        <AdBanner slot="supplements-browse-bottom" format="auto" className="mt-8" />
      </section>
    </>
  );
}
