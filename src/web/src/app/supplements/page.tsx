import type { Metadata } from "next";
import Link from "next/link";
import { searchSupplements } from "@/lib/api/supplements";
import { Breadcrumbs } from "@/components/common/Breadcrumbs";
import { AdBanner } from "@/components/ads/AdBanner";

export const metadata: Metadata = {
  title: "건강기능식품 목록 — A-Z 인덱스",
  description:
    "PillRight에 등록된 건강기능식품을 가나다순으로 찾아보세요. 기능성, 성분, 섭취방법 정보를 확인할 수 있습니다.",
  openGraph: {
    title: "건강기능식품 목록 — PillRight",
    description: "건강기능식품 가나다순 인덱스",
    type: "website",
  },
};

const CHOSUNG = [
  "ㄱ", "ㄴ", "ㄷ", "ㄹ", "ㅁ", "ㅂ", "ㅅ",
  "ㅇ", "ㅈ", "ㅊ", "ㅋ", "ㅌ", "ㅍ", "ㅎ",
] as const;

const ALPHA = "ABCDEFGHIJKLMNOPQRSTUVWXYZ".split("");

function getChosungIndex(char: string): number {
  const code = char.charCodeAt(0);
  if (code < 0xAC00 || code > 0xD7A3) return -1;
  const chosungMap = [0, 1, 2, 3, 4, 5, 6, 6, 7, 7, 7, 8, 9, 9, 10, 11, 12, 13, 13];
  return chosungMap[Math.floor((code - 0xAC00) / 588)] ?? -1;
}

interface SuppIndexItem {
  id: number;
  product_name: string;
  slug: string;
  company: string | null;
  category: string | null;
}

export default async function SupplementsIndexPage() {
  let allSupps: SuppIndexItem[] = [];

  try {
    const res = await searchSupplements("", 1, 200);
    allSupps = res.items.map((s) => ({
      id: s.id,
      product_name: s.product_name,
      slug: s.slug,
      company: s.company,
      category: s.category,
    }));
  } catch {
    /* API 미연결 시 빈 목록 */
  }

  const groups = new Map<string, SuppIndexItem[]>();

  for (const supp of allSupps) {
    const firstChar = supp.product_name.charAt(0).toUpperCase();
    let key: string;

    const ci = getChosungIndex(firstChar);
    if (ci >= 0) {
      key = CHOSUNG[ci];
    } else if (/[A-Z]/.test(firstChar)) {
      key = firstChar;
    } else {
      key = "#";
    }

    if (!groups.has(key)) groups.set(key, []);
    groups.get(key)!.push(supp);
  }

  const allKeys = [...CHOSUNG, ...ALPHA, "#"];
  const activeKeys = allKeys.filter((k) => groups.has(k));

  return (
    <>
      <Breadcrumbs
        items={[
          { label: "홈", href: "/" },
          { label: "건강기능식품 목록" },
        ]}
      />

      <section className="max-w-3xl mx-auto px-4 py-6">
        <h1 className="text-2xl font-bold text-[var(--color-primary)] mb-2">건강기능식품 목록</h1>
        <p className="text-gray-500 mb-6">
          가나다순·알파벳순으로 건강기능식품을 찾아보세요. 상세 페이지에서 기능성, 성분, 섭취방법을 확인할 수 있습니다.
        </p>

        {/* 검색 유도 */}
        <Link
          href="/check"
          className="block w-full p-4 mb-8 rounded-xl bg-[var(--color-primary-50)] border border-[var(--color-primary-100)] text-center hover:bg-[var(--color-primary-50)]/80 transition-colors"
        >
          <p className="text-sm font-medium text-[var(--color-primary)]">
            찾으시는 영양제가 있으신가요? →{" "}
            <span className="underline">상호작용 체크에서 검색하기</span>
          </p>
        </Link>

        {/* 인덱스 바 */}
        <nav className="flex flex-wrap gap-1 mb-8 sticky top-16 bg-[var(--color-bg)] py-2 z-10" aria-label="가나다 인덱스">
          {allKeys.map((key) => {
            const isActive = activeKeys.includes(key);
            return (
              <a
                key={key}
                href={isActive ? `#index-${key}` : undefined}
                className={`w-8 h-8 flex items-center justify-center rounded-lg text-xs font-medium transition-colors ${
                  isActive
                    ? "bg-[var(--color-primary)] text-white hover:bg-[var(--color-primary-dark)]"
                    : "bg-gray-100 text-gray-300 cursor-default"
                }`}
                onClick={isActive ? (e) => {
                  e.preventDefault();
                  document.getElementById(`index-${key}`)?.scrollIntoView({ behavior: "smooth" });
                } : undefined}
              >
                {key}
              </a>
            );
          })}
        </nav>

        {/* 그룹별 목록 */}
        <div className="space-y-8">
          {activeKeys.map((key) => (
            <div key={key} id={`index-${key}`} className="scroll-mt-28">
              <h2 className="text-lg font-bold text-[var(--color-primary)] border-b border-[var(--color-primary-100)] pb-1 mb-3">
                {key}
              </h2>
              <ul className="grid gap-1 sm:grid-cols-2">
                {groups.get(key)!.map((supp) => (
                  <li key={supp.id}>
                    <Link
                      href={`/supplements/${supp.slug}`}
                      className="block px-3 py-2 rounded-lg hover:bg-[var(--color-primary-50)] transition-colors"
                    >
                      <span className="text-sm font-medium text-gray-900">{supp.product_name}</span>
                      {supp.company && (
                        <span className="ml-2 text-xs text-gray-400">{supp.company}</span>
                      )}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        {allSupps.length === 0 && (
          <div className="text-center py-16 text-gray-400">
            건강기능식품 데이터를 불러올 수 없습니다. 나중에 다시 시도해주세요.
          </div>
        )}

        <AdBanner slot="supplements-index-bottom" format="auto" className="mt-8" />
      </section>
    </>
  );
}
