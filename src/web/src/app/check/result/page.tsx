import type { Metadata } from "next";
import Link from "next/link";
import { checkInteractions } from "@/lib/api/interactions";
import { ResultSummaryCard } from "@/components/result/ResultSummaryCard";
import { InteractionCard } from "@/components/result/InteractionCard";
import { AdBanner } from "@/components/ads/AdBanner";
import type { InteractionCheckItem } from "@/types/interaction";

interface PageProps {
  searchParams: Promise<{ items?: string }>;
}

function parseItems(raw: string): { checkItems: InteractionCheckItem[]; names: Map<string, string> } {
  const checkItems: InteractionCheckItem[] = [];
  const names = new Map<string, string>();

  for (const segment of raw.split(",")) {
    const [type, id, name] = segment.split(":");
    if ((type === "drug" || type === "supplement") && id && name) {
      checkItems.push({ item_type: type, item_id: Number(id) });
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
    description: `${nameList.join(", ")} 복약 상호작용 체크 결과 — 약먹어에서 확인하세요.`,
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
        <p className="text-gray-500 mb-4">확인할 항목이 부족합니다. 2개 이상 선택해주세요.</p>
        <Link
          href="/check"
          className="inline-block px-6 py-2 rounded-lg text-white font-semibold bg-[var(--color-brand)] hover:bg-[var(--color-brand-dark)]"
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
    error = e instanceof Error ? e.message : "상호작용 확인 중 오류가 발생했습니다.";
  }

  if (error || !data) {
    return (
      <section className="max-w-2xl mx-auto px-4 py-16 text-center">
        <p className="text-red-600 mb-4">{error}</p>
        <Link
          href="/check"
          className="inline-block px-6 py-2 rounded-lg text-white font-semibold bg-[var(--color-brand)] hover:bg-[var(--color-brand-dark)]"
        >
          다시 시도하기
        </Link>
      </section>
    );
  }

  return (
    <section className="max-w-2xl mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold text-gray-900 mb-6">상호작용 체크 결과</h1>

      <div className="space-y-4">
        <ResultSummaryCard data={data} />

        {data.results.length > 0 && (
          <div className="space-y-3">
            <h2 className="text-lg font-semibold text-gray-900">상세 결과</h2>
            {data.results.map((r, i) => (
              <InteractionCard key={i} interaction={r} />
            ))}
          </div>
        )}

        <div className="bg-amber-50 border border-amber-200 rounded-lg p-4 text-sm text-amber-700">
          <p className="font-medium mb-1">면책조항</p>
          <p>{data.disclaimer || "이 정보는 참고용이며, 의사/약사의 전문적 판단을 대체하지 않습니다. 반드시 전문가와 상담하세요."}</p>
        </div>

        {/* 광고 */}
        <AdBanner slot="check-result-bottom" format="auto" />

        <div className="flex gap-3">
          <Link
            href="/check"
            className="flex-1 py-3 rounded-lg text-center font-semibold border border-gray-300 text-gray-700 hover:bg-gray-50"
          >
            다시 체크하기
          </Link>
        </div>
      </div>
    </section>
  );
}
