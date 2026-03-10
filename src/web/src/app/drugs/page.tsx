import type { Metadata } from "next";
import Link from "next/link";
import { getDrugBrowseCounts } from "@/lib/api/drugs";
import { Breadcrumbs } from "@/components/common/Breadcrumbs";
import { AdBanner } from "@/components/ads/AdBanner";
import { CHOSUNG, ALPHA } from "@/lib/utils/korean";
import { QuickSearch } from "@/components/common/QuickSearch";

export const metadata: Metadata = {
  title: "의약품 목록 — A-Z 인덱스",
  description:
    "약잘알에 등록된 의약품을 가나다순으로 찾아보세요. 효능, 용법, 상호작용 정보를 확인할 수 있습니다.",
  openGraph: {
    title: "의약품 목록 — 약잘알",
    description: "의약품 가나다순 인덱스",
    type: "website",
  },
};

export const revalidate = 86400; // 24시간마다 갱신

export default async function DrugsIndexPage() {
  let counts: Record<string, number> = {};

  try {
    counts = await getDrugBrowseCounts();
  } catch (err) {
    console.error("[drugs/page] getDrugBrowseCounts failed:", err);
  }

  const totalCount = Object.values(counts).reduce((a, b) => a + b, 0);

  return (
    <>
      <Breadcrumbs
        items={[
          { label: "홈", href: "/" },
          { label: "의약품 목록" },
        ]}
      />

      <section className="max-w-3xl mx-auto px-4 py-6">
        <h1 className="text-2xl font-bold text-[var(--color-primary)] mb-2">의약품 목록</h1>
        <p className="text-gray-500 mb-6">
          총 {totalCount.toLocaleString()}개의 의약품을 가나다순·알파벳순으로 찾아보세요.
          상세 페이지에서 효능, 용법, 상호작용을 확인할 수 있습니다.
        </p>

        {/* 바로 검색 */}
        <QuickSearch type="drug" />

        {/* 초성/알파벳 인덱스 그리드 */}
        <div className="space-y-6">
          {/* 한글 초성 */}
          <div>
            <h2 className="text-sm font-semibold text-gray-500 mb-3">한글 (가나다)</h2>
            <div className="grid grid-cols-5 sm:grid-cols-7 gap-1.5 sm:gap-2">
              {CHOSUNG.map((key) => {
                const count = counts[key] ?? 0;
                const hasItems = count > 0;
                return hasItems ? (
                  <Link
                    key={key}
                    href={`/drugs/browse/${encodeURIComponent(key)}`}
                    className="flex flex-col items-center justify-center rounded-xl p-2 sm:p-3 bg-[var(--color-primary-50)] hover:bg-[var(--color-primary-100)]/40 transition-colors border border-[var(--color-primary-100)]"
                  >
                    <span className="text-base sm:text-lg font-bold text-[var(--color-primary)]">{key}</span>
                    <span className="text-[11px] sm:text-xs text-gray-500 mt-0.5 sm:mt-1">{count.toLocaleString()}</span>
                  </Link>
                ) : (
                  <div
                    key={key}
                    className="flex flex-col items-center justify-center rounded-xl p-2 sm:p-3 bg-gray-50 border border-gray-100"
                  >
                    <span className="text-base sm:text-lg font-bold text-gray-300">{key}</span>
                    <span className="text-[11px] sm:text-xs text-gray-300 mt-0.5 sm:mt-1">0</span>
                  </div>
                );
              })}
            </div>
          </div>

          {/* 알파벳 */}
          <div>
            <h2 className="text-sm font-semibold text-gray-500 mb-3">알파벳 (A-Z)</h2>
            <div className="grid grid-cols-5 sm:grid-cols-7 md:grid-cols-9 gap-1.5 sm:gap-2">
              {ALPHA.map((key) => {
                const count = counts[key] ?? 0;
                const hasItems = count > 0;
                return hasItems ? (
                  <Link
                    key={key}
                    href={`/drugs/browse/${encodeURIComponent(key)}`}
                    className="flex flex-col items-center justify-center rounded-xl p-2 sm:p-3 bg-[var(--color-primary-50)] hover:bg-[var(--color-primary-100)]/40 transition-colors border border-[var(--color-primary-100)]"
                  >
                    <span className="text-base sm:text-lg font-bold text-[var(--color-primary)]">{key}</span>
                    <span className="text-[11px] sm:text-xs text-gray-500 mt-0.5 sm:mt-1">{count.toLocaleString()}</span>
                  </Link>
                ) : (
                  <div
                    key={key}
                    className="flex flex-col items-center justify-center rounded-xl p-2 sm:p-3 bg-gray-50 border border-gray-100"
                  >
                    <span className="text-base sm:text-lg font-bold text-gray-300">{key}</span>
                    <span className="text-[11px] sm:text-xs text-gray-300 mt-0.5 sm:mt-1">0</span>
                  </div>
                );
              })}
            </div>
          </div>
        </div>

        {totalCount === 0 && (
          <div className="text-center py-16 text-gray-400">
            의약품 데이터를 불러올 수 없습니다. 나중에 다시 시도해주세요.
          </div>
        )}

        <AdBanner slot="drugs-index-bottom" format="auto" className="mt-8" />
      </section>
    </>
  );
}
