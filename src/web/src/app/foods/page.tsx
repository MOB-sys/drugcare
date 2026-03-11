import type { Metadata } from "next";
import { Breadcrumbs } from "@/components/common/Breadcrumbs";
import { AdBanner } from "@/components/ads/AdBanner";
import { getAllFoods } from "@/lib/api/foods";
import type { FoodSearchItem } from "@/types/food";
import { FoodListClient } from "./FoodListClient";
import { SITE_URL } from "@/lib/constants/site";

export const metadata: Metadata = {
  title: "식품 목록 — 약물 상호작용이 있는 식품",
  description:
    "약물과 상호작용이 알려진 주요 식품을 카테고리별로 찾아보세요. 자몽, 우유, 커피 등 복약 시 주의해야 할 식품 정보를 확인할 수 있습니다.",
  alternates: { canonical: "/foods" },
  openGraph: {
    title: "식품 목록 — 약잘알",
    description: "약물 상호작용이 있는 식품 카테고리별 인덱스",
    type: "website",
  },
};

export const revalidate = 86400;

/** 카테고리별 메타 정보. */
const CATEGORY_META: Record<string, { icon: string; color: string }> = {
  과일: { icon: "🍊", color: "bg-orange-100 dark:bg-orange-900/30 text-orange-700 dark:text-orange-300" },
  채소: { icon: "🥬", color: "bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300" },
  유제품: { icon: "🥛", color: "bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300" },
  음료: { icon: "☕", color: "bg-amber-100 dark:bg-amber-900/30 text-amber-700 dark:text-amber-300" },
  곡류: { icon: "🌾", color: "bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-300" },
  견과류: { icon: "🥜", color: "bg-stone-100 dark:bg-stone-900/30 text-stone-700 dark:text-stone-300" },
  해산물: { icon: "🐟", color: "bg-cyan-100 dark:bg-cyan-900/30 text-cyan-700 dark:text-cyan-300" },
  육류: { icon: "🥩", color: "bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-300" },
  "조미료/향신료": { icon: "🧄", color: "bg-lime-100 dark:bg-lime-900/30 text-lime-700 dark:text-lime-300" },
  발효식품: { icon: "🫙", color: "bg-purple-100 dark:bg-purple-900/30 text-purple-700 dark:text-purple-300" },
};

const DEFAULT_META = { icon: "🍽️", color: "bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300" };

export default async function FoodsIndexPage() {
  let items: FoodSearchItem[] = [];
  try {
    const result = await getAllFoods(1, 100);
    items = result.items;
  } catch {
    /* 빌드 시 API 미연결 대비 */
  }

  /* 카테고리 목록 추출 + 아이템 수 계산 */
  const categoryMap = new Map<string, FoodSearchItem[]>();
  for (const item of items) {
    const cat = item.category || "기타";
    if (!categoryMap.has(cat)) categoryMap.set(cat, []);
    categoryMap.get(cat)!.push(item);
  }
  const categories = Array.from(categoryMap.keys());

  const jsonLd = {
    "@context": "https://schema.org",
    "@type": "CollectionPage",
    name: "약물 상호작용이 있는 식품 목록",
    description: `약물과 상호작용이 알려진 ${items.length}종의 식품 카테고리별 목록`,
    url: `${SITE_URL}/foods`,
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
          { label: "식품 목록" },
        ]}
      />

      <section className="max-w-4xl mx-auto px-4 py-6">
        <h1 className="text-2xl font-bold text-[var(--color-primary)] mb-2">
          식품 목록
        </h1>
        <p className="text-gray-500 dark:text-gray-400 mb-6">
          {items.length > 0
            ? `약물과 상호작용이 알려진 ${items.length}종의 식품을 카테고리별로 확인하세요.`
            : "약물과 상호작용이 알려진 주요 식품을 카테고리별로 확인하세요."}
          {" "}각 식품을 클릭하면 상세 정보와 상호작용을 확인할 수 있습니다.
        </p>

        <FoodListClient
          items={items}
          categories={categories}
          categoryMeta={CATEGORY_META}
          defaultMeta={DEFAULT_META}
        />

        <AdBanner slot="foods-index-bottom" format="auto" className="mt-8" />

        <p className="mt-6 text-xs text-gray-400 dark:text-gray-500 text-center">
          본 정보는 참고용이며, 의사/약사의 전문적 판단을 대체하지 않습니다.
        </p>
      </section>
    </>
  );
}
