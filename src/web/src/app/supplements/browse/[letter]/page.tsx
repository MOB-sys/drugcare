import type { Metadata } from "next";
import Link from "next/link";
import { browseSupplementsByLetter } from "@/lib/api/supplements";
import { Breadcrumbs } from "@/components/common/Breadcrumbs";
import { Pagination } from "@/components/common/Pagination";
import { AdBanner } from "@/components/ads/AdBanner";
import { ALL_LETTERS, CHOSUNG } from "@/lib/utils/korean";

export const revalidate = 86400; // 24시간 ISR

const PAGE_SIZE = 50;

interface PageProps {
  params: Promise<{ letter: string }>;
  searchParams: Promise<{ page?: string }>;
}

export function generateStaticParams() {
  return ALL_LETTERS.map((letter) => ({ letter }));
}

export async function generateMetadata({ params }: PageProps): Promise<Metadata> {
  const { letter: rawLetter } = await params;
  const letter = decodeURIComponent(rawLetter);
  const particle = (CHOSUNG as readonly string[]).includes(letter) ? "으로" : "로";
  const title = `${letter}${particle} 시작하는 건강기능식품 목록`;
  return {
    title,
    description: `${letter}${particle} 시작하는 건강기능식품을 찾아보세요. 기능성, 성분, 섭취방법 정보를 확인할 수 있습니다.`,
    alternates: { canonical: `/supplements/browse/${encodeURIComponent(letter)}` },
  };
}

export default async function SupplementBrowsePage({ params, searchParams }: PageProps) {
  const { letter: rawLetter } = await params;
  const letter = decodeURIComponent(rawLetter);
  const { page: pageStr } = await searchParams;
  const currentPage = Math.max(1, parseInt(pageStr ?? "1", 10) || 1);
  const particle = (CHOSUNG as readonly string[]).includes(letter) ? "으로" : "로";

  let items: Array<{
    id: number;
    product_name: string;
    slug: string;
    company: string | null;
  }> = [];
  let total = 0;
  let totalPages = 0;

  try {
    const res = await browseSupplementsByLetter(letter, currentPage, PAGE_SIZE);
    items = res.items.map((s) => ({
      id: s.id,
      product_name: s.product_name,
      slug: s.slug,
      company: s.company,
    }));
    total = res.total;
    totalPages = Math.ceil(res.total / PAGE_SIZE);
  } catch {
    /* API 미연결 시 빈 목록 */
  }

  const encodedLetter = encodeURIComponent(letter);

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
          총 {total.toLocaleString()}개의 건강기능식품이 있습니다.
          {totalPages > 1 && ` (${currentPage}/${totalPages} 페이지)`}
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
                  : "bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-300 hover:bg-[var(--color-primary-50)]"
              }`}
            >
              {l}
            </Link>
          ))}
        </nav>

        {/* 건강기능식품 목록 */}
        {items.length > 0 ? (
          <ul className="grid gap-1 sm:grid-cols-2">
            {items.map((supp) => (
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

        {/* 페이지네이션 */}
        <Pagination
          currentPage={currentPage}
          totalPages={totalPages}
          basePath={`/supplements/browse/${encodedLetter}?page={page}`}
        />

        <AdBanner slot="supplements-browse-bottom" format="auto" className="mt-8" />
      </section>
    </>
  );
}
