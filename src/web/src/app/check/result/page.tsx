import type { Metadata } from "next";
import Link from "next/link";
import { checkInteractions } from "@/lib/api/interactions";
import { ResultSummaryCard } from "@/components/result/ResultSummaryCard";
import { InteractionCard } from "@/components/result/InteractionCard";
import { AdBanner } from "@/components/ads/AdBanner";
import { Breadcrumbs } from "@/components/common/Breadcrumbs";
import { ShareActions } from "@/components/result/ShareActions";
import { AppPromotionCTA } from "@/components/result/AppPromotionCTA";
import type { InteractionCheckItem } from "@/types/interaction";

interface PageProps {
  searchParams: Promise<{ items?: string }>;
}

function parseItems(raw: string): { checkItems: InteractionCheckItem[]; names: Map<string, string> } {
  const checkItems: InteractionCheckItem[] = [];
  const names = new Map<string, string>();

  for (const segment of raw.split(",")) {
    const [type, id, ...nameParts] = segment.split(":");
    const name = nameParts.join(":");
    const numId = Number(id);
    if ((type === "drug" || type === "supplement" || type === "food" || type === "herbal") && id && name && !Number.isNaN(numId) && Number.isInteger(numId) && numId > 0) {
      checkItems.push({ item_type: type, item_id: numId });
      names.set(`${type}:${id}`, decodeURIComponent(name));
    }
  }
  return { checkItems, names };
}

export async function generateMetadata({ searchParams }: PageProps): Promise<Metadata> {
  const params = await searchParams;
  const raw = params.items ?? "";
  const { names } = parseItems(raw);
  const nameList = [...names.values()];

  const title =
    nameList.length >= 2
      ? `${nameList[0]} + ${nameList[1]} 상호작용 결과`
      : "상호작용 체크 결과";

  return {
    title,
    description: `${nameList.join(", ")} 복약 상호작용 체크 결과 — 약잘알에서 확인하세요.`,
    openGraph: { title, type: "article" },
  };
}

export default async function CheckResultPage({ searchParams }: PageProps) {
  const params = await searchParams;
  const raw = params.items ?? "";
  const { checkItems } = parseItems(raw);

  if (checkItems.length < 2) {
    return (
      <section className="max-w-2xl mx-auto px-4 py-16 text-center">
        <p className="text-gray-500 dark:text-gray-400 mb-4">확인할 항목이 부족합니다. 2개 이상 선택해주세요.</p>
        <Link
          href="/check"
          className="inline-block px-6 py-2 rounded-xl text-white font-semibold bg-[var(--color-primary)] hover:bg-[var(--color-primary-dark)]"
        >
          다시 선택하기
        </Link>
      </section>
    );
  }

  let data;
  let error: string | null = null;

  try {
    data = await checkInteractions(checkItems);
  } catch (e) {
    error = "상호작용 확인 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요.";
  }

  if (error || !data) {
    return (
      <section className="max-w-2xl mx-auto px-4 py-16 text-center">
        <p className="text-red-600 mb-4">{error}</p>
        <Link
          href="/check"
          className="inline-block px-6 py-2 rounded-xl text-white font-semibold bg-[var(--color-primary)] hover:bg-[var(--color-primary-dark)]"
        >
          다시 시도하기
        </Link>
      </section>
    );
  }

  return (
    <>
      <Breadcrumbs
        items={[
          { label: "홈", href: "/" },
          { label: "상호작용 체크", href: "/check" },
          { label: "결과" },
        ]}
      />

      <section className="max-w-2xl mx-auto px-4 py-6">
        <h1 className="text-2xl font-bold text-[var(--color-primary)] mb-6">상호작용 체크 결과</h1>

        <div className="space-y-4">
          <ResultSummaryCard data={data} />

          {data.results.length > 0 && (
            <div className="space-y-3">
              <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100">상세 결과</h2>
              {data.results.map((r, i) => (
                <InteractionCard key={`${r.item_a_name}-${r.item_b_name}-${i}`} interaction={r} />
              ))}
            </div>
          )}

          <div className="bg-[var(--color-primary-50)] border border-[var(--color-primary-100)] rounded-xl p-4 text-sm text-[var(--color-primary)]">
            <div className="flex gap-2">
              <svg className="w-4 h-4 mt-0.5 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <div>
                <p className="font-medium mb-1">면책조항</p>
                <p className="text-[var(--color-primary)]/80">{data.disclaimer || "이 정보는 참고용이며, 의사/약사의 전문적 판단을 대체하지 않습니다. 반드시 전문가와 상담하세요."}</p>
              </div>
            </div>
          </div>

          {/* 공유/인쇄 */}
          <div className="flex items-center justify-between">
            <ShareActions />
          </div>

          {/* 앱 유도 */}
          <AppPromotionCTA />

          {/* 광고 */}
          <AdBanner slot="check-result-bottom" format="auto" />

          <div className="flex gap-3">
            <Link
              href="/check"
              className="flex-1 py-3 rounded-xl text-center font-semibold border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-200 hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
            >
              다시 체크하기
            </Link>
          </div>
        </div>
      </section>
    </>
  );
}
