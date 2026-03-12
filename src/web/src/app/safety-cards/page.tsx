import type { Metadata } from "next";
import Link from "next/link";
import Image from "next/image";
import { Breadcrumbs } from "@/components/common/Breadcrumbs";
import { AdBanner } from "@/components/ads/AdBanner";
import { SITE_URL } from "@/lib/constants/site";
import indexData from "./data";

export const metadata: Metadata = {
  title: "약물 상호작용 안전 카드 — 꼭 알아야 할 위험한 조합",
  description:
    "해열제+술, 와파린+비타민K 등 자주 발생하는 약물 상호작용을 시각 카드로 한눈에 확인하세요. 식약처 DUR 데이터 기반.",
  keywords: [
    "약물 상호작용",
    "약 같이 먹으면",
    "해열제 술",
    "와파린 비타민K",
    "약 부작용",
    "복약 안전",
  ],
  openGraph: {
    title: "약물 상호작용 안전 카드 — 약잘알",
    description: "자주 발생하는 위험한 약물 조합을 시각 카드로 확인하세요.",
    type: "website",
    url: `${SITE_URL}/safety-cards`,
  },
};

function severityBadge(severity: string, score: number) {
  const colors =
    severity === "high"
      ? "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400"
      : severity === "moderate"
        ? "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400"
        : "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400";

  const label = severity === "high" ? "높음" : severity === "moderate" ? "보통" : "낮음";

  return (
    <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-semibold ${colors}`}>
      위험도 {score}/10 · {label}
    </span>
  );
}

export default function SafetyCardsPage() {
  const items = indexData.items;

  // 위험도 높은 순 정렬
  const sorted = [...items].sort((a, b) => b.danger_score - a.danger_score);

  return (
    <>
      <Breadcrumbs
        items={[
          { label: "홈", href: "/" },
          { label: "안전 카드" },
        ]}
      />

      <section className="max-w-4xl mx-auto px-4 py-6">
        <h1 className="text-2xl font-bold text-[var(--color-primary)] mb-2">
          약물 상호작용 안전 카드
        </h1>
        <p className="text-gray-500 dark:text-gray-400 mb-6">
          자주 발생하는 위험한 약물 조합을 시각 카드로 한눈에 확인하세요.
          식약처 DUR 데이터를 기반으로 제작되었습니다.
        </p>

        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3">
          {sorted.map((item) => (
            <Link
              key={item.id}
              href={`/safety-cards/${item.id}`}
              className="group rounded-xl overflow-hidden border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 shadow-sm hover:shadow-md transition-shadow"
            >
              <div className="relative aspect-[9/16] bg-gray-100 dark:bg-gray-900">
                <Image
                  src={`/sns-content/${item.thumb}`}
                  alt={item.title}
                  fill
                  sizes="(max-width: 640px) 50vw, (max-width: 768px) 33vw, 25vw"
                  className="object-cover group-hover:scale-105 transition-transform duration-300"
                />
              </div>
              <div className="p-2.5">
                {severityBadge(item.severity, item.danger_score)}
                <p className="mt-1.5 text-sm font-medium text-gray-900 dark:text-gray-100 line-clamp-2 leading-tight">
                  {item.title.replace(" — 같이 먹어도 될까?", "")}
                </p>
              </div>
            </Link>
          ))}
        </div>

        <AdBanner slot="safety-cards-bottom" format="auto" className="mt-6" />

        <div className="mt-6 p-4 rounded-xl bg-[var(--color-primary-50)] border border-[var(--color-primary-100)] text-sm text-[var(--color-primary)]">
          <p className="font-medium mb-1">면책조항</p>
          <p className="opacity-80">
            이 정보는 식약처 DUR 데이터를 기반으로 한 참고 자료이며, 의사/약사의 전문적 판단을 대체하지 않습니다.
          </p>
        </div>
      </section>
    </>
  );
}
