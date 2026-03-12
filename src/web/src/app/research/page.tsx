import type { Metadata } from "next";
import Link from "next/link";
import { getAllResearch } from "@/lib/content/loader";
import { Breadcrumbs } from "@/components/common/Breadcrumbs";
import { AdBanner } from "@/components/ads/AdBanner";

export const metadata: Metadata = {
  title: "최신 연구 — 약물 안전 연구 요약 | 약잘알",
  description: "최신 의학 논문에서 발췌한 약물 상호작용, 영양제 효능, 복약 안전 연구 요약을 확인하세요.",
  alternates: { canonical: "/research" },
};

const EVIDENCE_BADGE: Record<string, string> = {
  high: "bg-green-50 dark:bg-green-900/30 text-green-700 dark:text-green-400",
  moderate: "bg-amber-50 dark:bg-amber-900/30 text-amber-700 dark:text-amber-400",
  low: "bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300",
};

const EVIDENCE_LABELS: Record<string, string> = {
  high: "높은 근거", moderate: "보통 근거", low: "낮은 근거",
};

export default function ResearchPage() {
  const research = getAllResearch();

  return (
    <>
      <Breadcrumbs items={[{ label: "홈", href: "/" }, { label: "최신 연구" }]} />

      <section className="max-w-3xl mx-auto px-4 py-6">
        <h1 className="text-2xl font-bold text-[var(--color-primary)] mb-2">최신 연구</h1>
        <p className="text-gray-500 dark:text-gray-400 mb-6">
          최신 의학 논문에서 발췌한 약물 안전 연구 요약입니다.
        </p>

        {research.length === 0 ? (
          <p className="text-center py-12 text-gray-400 dark:text-gray-500 text-sm">
            아직 등록된 연구 요약이 없습니다.
          </p>
        ) : (
          <div className="space-y-4">
            {research.map((item) => (
              <Link
                key={item.slug}
                href={`/research/${item.slug}`}
                className="group block bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-700 p-5 shadow-sm hover:shadow-md hover:border-[var(--color-primary-100)] transition-all"
              >
                <div className="flex items-start gap-3">
                  <div className="min-w-0 flex-1">
                    <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-1.5 break-keep group-hover:text-[var(--color-primary)] transition-colors">
                      {item.title}
                    </h2>
                    <p className="text-sm text-gray-500 dark:text-gray-400 line-clamp-2 mb-2">
                      {item.description}
                    </p>
                    <div className="flex flex-wrap items-center gap-2 text-xs">
                      {item.journal && (
                        <span className="text-gray-400 dark:text-gray-500 italic">{item.journal}</span>
                      )}
                      {item.evidenceLevel && (
                        <span className={`px-2 py-0.5 rounded-full font-medium ${EVIDENCE_BADGE[item.evidenceLevel] ?? EVIDENCE_BADGE.low}`}>
                          {EVIDENCE_LABELS[item.evidenceLevel] ?? item.evidenceLevel}
                        </span>
                      )}
                      <span className="text-gray-400 dark:text-gray-500">{item.publishedAt}</span>
                    </div>
                  </div>
                </div>
              </Link>
            ))}
          </div>
        )}

        <AdBanner slot="research-list-bottom" format="auto" className="mt-6" />

        <p className="text-xs text-gray-400 dark:text-gray-500 text-center mt-6">
          이 정보는 의학 논문의 요약이며, 의사/약사의 전문적 판단을 대체하지 않습니다.
        </p>
      </section>
    </>
  );
}
