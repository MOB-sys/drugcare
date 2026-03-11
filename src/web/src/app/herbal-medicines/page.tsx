import type { Metadata } from "next";
import { Breadcrumbs } from "@/components/common/Breadcrumbs";
import { AdBanner } from "@/components/ads/AdBanner";
import { getAllHerbalMedicines } from "@/lib/api/herbal";
import type { HerbalMedicineSearchItem } from "@/types/herbal";
import { HerbalListClient } from "./HerbalListClient";
import { SITE_URL } from "@/lib/constants/site";

export const metadata: Metadata = {
  title: "한약재 목록 — 대한약전 기반 생약 정보",
  description:
    "대한약전 기반 주요 한약재를 분류별로 찾아보세요. 인삼, 당귀, 황기 등 한약재의 효능, 주의사항, 약물 상호작용 정보를 확인할 수 있습니다.",
  alternates: { canonical: "/herbal-medicines" },
  openGraph: {
    title: "한약재 목록 — 약잘알",
    description: "대한약전 기반 한약재 분류별 인덱스",
    type: "website",
  },
};

export const revalidate = 86400;

/** 카테고리별 메타 정보. */
const CATEGORY_META: Record<string, { icon: string; color: string; desc: string }> = {
  보기약: { icon: "💛", color: "bg-amber-100 dark:bg-amber-900/30 text-amber-700 dark:text-amber-300", desc: "기(氣)를 보하는 약재" },
  보혈약: { icon: "❤️", color: "bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-300", desc: "혈(血)을 보하는 약재" },
  보음약: { icon: "💧", color: "bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300", desc: "음(陰)을 자양하는 약재" },
  보양약: { icon: "🔥", color: "bg-orange-100 dark:bg-orange-900/30 text-orange-700 dark:text-orange-300", desc: "양(陽)을 보하는 약재" },
  해표약: { icon: "💨", color: "bg-sky-100 dark:bg-sky-900/30 text-sky-700 dark:text-sky-300", desc: "체표의 사기를 발산하는 약재" },
  청열약: { icon: "🧊", color: "bg-teal-100 dark:bg-teal-900/30 text-teal-700 dark:text-teal-300", desc: "열을 식히고 해독하는 약재" },
  거풍습약: { icon: "🌿", color: "bg-emerald-100 dark:bg-emerald-900/30 text-emerald-700 dark:text-emerald-300", desc: "풍습을 제거하는 약재" },
  이수삼습약: { icon: "💦", color: "bg-cyan-100 dark:bg-cyan-900/30 text-cyan-700 dark:text-cyan-300", desc: "수습 제거 · 이뇨 약재" },
  활혈거어약: { icon: "🩸", color: "bg-rose-100 dark:bg-rose-900/30 text-rose-700 dark:text-rose-300", desc: "혈액순환 · 어혈 제거 약재" },
  지혈약: { icon: "🩹", color: "bg-pink-100 dark:bg-pink-900/30 text-pink-700 dark:text-pink-300", desc: "출혈을 멎게 하는 약재" },
  안신약: { icon: "🌙", color: "bg-indigo-100 dark:bg-indigo-900/30 text-indigo-700 dark:text-indigo-300", desc: "마음 안정 · 수면 약재" },
};

const DEFAULT_META = { icon: "🌱", color: "bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300", desc: "기타 한약재" };

export default async function HerbalMedicinesIndexPage() {
  let items: HerbalMedicineSearchItem[] = [];
  try {
    const result = await getAllHerbalMedicines(1, 100);
    items = result.items;
  } catch {
    /* 빌드 시 API 미연결 대비 */
  }

  const categoryMap = new Map<string, HerbalMedicineSearchItem[]>();
  for (const item of items) {
    const cat = item.category || "기타";
    if (!categoryMap.has(cat)) categoryMap.set(cat, []);
    categoryMap.get(cat)!.push(item);
  }
  const categories = Array.from(categoryMap.keys());

  const jsonLd = {
    "@context": "https://schema.org",
    "@type": "CollectionPage",
    name: "대한약전 기반 한약재 목록",
    description: `대한약전 기반 ${items.length}종의 한약재 분류별 목록`,
    url: `${SITE_URL}/herbal-medicines`,
    isPartOf: { "@type": "WebSite", name: "약잘알", url: SITE_URL },
    numberOfItems: items.length,
  };

  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
      />
      <Breadcrumbs
        items={[
          { label: "홈", href: "/" },
          { label: "한약재 목록" },
        ]}
      />

      <section className="max-w-4xl mx-auto px-4 py-6">
        <h1 className="text-2xl font-bold text-[var(--color-primary)] mb-2">
          한약재 목록
        </h1>
        <p className="text-gray-500 dark:text-gray-400 mb-6">
          {items.length > 0
            ? `대한약전 기반 ${items.length}종의 한약재를 분류별로 확인하세요.`
            : "대한약전 기반 주요 한약재를 분류별로 확인하세요."}
          {" "}각 한약재를 클릭하면 효능, 주의사항, 약물 상호작용 정보를 볼 수 있습니다.
        </p>

        <HerbalListClient
          items={items}
          categories={categories}
          categoryMeta={CATEGORY_META}
          defaultMeta={DEFAULT_META}
        />

        <AdBanner slot="herbal-index-bottom" format="auto" className="mt-8" />

        <p className="mt-6 text-xs text-gray-400 dark:text-gray-500 text-center">
          본 정보는 참고용이며, 의사/약사의 전문적 판단을 대체하지 않습니다.
          한약재는 반드시 전문가의 처방에 따라 복용하세요.
        </p>
      </section>
    </>
  );
}
