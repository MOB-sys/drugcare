import type { Metadata } from "next";
import Link from "next/link";
import { searchDrugs } from "@/lib/api/drugs";
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
  const title = `${letter}${particle} 시작하는 의약품 목록`;
  return {
    title,
    description: `${letter}${particle} 시작하는 의약품을 찾아보세요. 효능, 용법, 상호작용 정보를 확인할 수 있습니다.`,
  };
}

export default async function DrugBrowsePage({ params }: PageProps) {
  const { letter } = await params;
  const particle = (CHOSUNG as readonly string[]).includes(letter) ? "으로" : "로";

  interface DrugItem {
    id: number;
    item_name: string;
    slug: string;
    entp_name: string | null;
  }

  let drugs: DrugItem[] = [];

  try {
    const res = await searchDrugs("", 1, 2000);
    drugs = res.items
      .filter((d) => matchesLetterKey(d.item_name, letter))
      .map((d) => ({ id: d.id, item_name: d.item_name, slug: d.slug, entp_name: d.entp_name }));
  } catch {
    /* API 미연결 시 빈 목록 */
  }

  return (
    <>
      <Breadcrumbs
        items={[
          { label: "홈", href: "/" },
          { label: "의약품 목록", href: "/drugs" },
          { label: `${letter} 의약품` },
        ]}
      />

      <section className="max-w-3xl mx-auto px-4 py-6">
        <h1 className="text-2xl font-bold text-[var(--color-primary)] mb-2">
          {letter}{particle} 시작하는 의약품
        </h1>
        <p className="text-[var(--color-text-secondary)] mb-6">
          총 {drugs.length}개의 의약품이 있습니다.
        </p>

        {/* 인덱스 네비게이션 */}
        <nav className="flex flex-wrap gap-1 mb-8" aria-label="가나다 인덱스">
          {ALL_LETTERS.map((l) => (
            <Link
              key={l}
              href={`/drugs/browse/${encodeURIComponent(l)}`}
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

        {/* 의약품 목록 */}
        {drugs.length > 0 ? (
          <ul className="grid gap-1 sm:grid-cols-2">
            {drugs.map((drug) => (
              <li key={drug.id}>
                <Link
                  href={`/drugs/${drug.slug}`}
                  className="block px-3 py-2 rounded-lg hover:bg-[var(--color-primary-50)] transition-colors"
                >
                  <span className="text-sm font-medium text-[var(--color-text)]">{drug.item_name}</span>
                  {drug.entp_name && (
                    <span className="ml-2 text-xs text-[var(--color-text-muted)]">{drug.entp_name}</span>
                  )}
                </Link>
              </li>
            ))}
          </ul>
        ) : (
          <div className="text-center py-16 text-[var(--color-text-muted)]">
            해당 글자로 시작하는 의약품이 없습니다.
          </div>
        )}

        <AdBanner slot="drugs-browse-bottom" format="auto" className="mt-8" />
      </section>
    </>
  );
}
