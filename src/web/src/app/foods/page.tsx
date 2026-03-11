import type { Metadata } from "next";
import { Breadcrumbs } from "@/components/common/Breadcrumbs";
import { AdBanner } from "@/components/ads/AdBanner";
import { getFoodCount } from "@/lib/api/foods";

export const metadata: Metadata = {
  title: "식품 목록 — 약물 상호작용이 있는 식품",
  description:
    "약물과 상호작용이 알려진 주요 식품을 카테고리별로 찾아보세요. 자몽, 우유, 커피 등 복약 시 주의해야 할 식품 정보를 확인할 수 있습니다.",
  openGraph: {
    title: "식품 목록 — 약잘알",
    description: "약물 상호작용이 있는 식품 카테고리별 인덱스",
    type: "website",
  },
};

export const revalidate = 86400;

/** 식품 카테고리 정적 데이터 — seed_foods.py 기반. */
const FOOD_CATEGORIES = [
  {
    name: "과일",
    icon: "🍊",
    description: "자몽, 바나나, 오렌지 등 CYP 효소 및 칼륨 관련 상호작용",
    examples: ["자몽", "바나나", "크랜베리", "아보카도"],
    color: "bg-orange-50 dark:bg-orange-900/20 border-orange-200 dark:border-orange-800",
    iconBg: "bg-orange-100 dark:bg-orange-900/30",
  },
  {
    name: "채소",
    icon: "🥬",
    description: "시금치, 케일, 브로콜리 등 비타민K 함유 채소와 항응고제 상호작용",
    examples: ["시금치", "케일", "브로콜리", "깻잎"],
    color: "bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-800",
    iconBg: "bg-green-100 dark:bg-green-900/30",
  },
  {
    name: "유제품",
    icon: "🥛",
    description: "우유, 치즈, 요거트 등 칼슘·티라민 관련 항생제·MAO 억제제 상호작용",
    examples: ["우유", "치즈", "요거트", "버터"],
    color: "bg-blue-50 dark:bg-blue-900/20 border-blue-200 dark:border-blue-800",
    iconBg: "bg-blue-100 dark:bg-blue-900/30",
  },
  {
    name: "음료",
    icon: "☕",
    description: "커피, 녹차, 알코올, 자몽주스 등 카페인·CYP·간 대사 관련 상호작용",
    examples: ["커피", "녹차", "알코올", "자몽주스"],
    color: "bg-amber-50 dark:bg-amber-900/20 border-amber-200 dark:border-amber-800",
    iconBg: "bg-amber-100 dark:bg-amber-900/30",
  },
  {
    name: "곡류",
    icon: "🌾",
    description: "귀리, 현미, 두부, 콩 등 식이섬유·이소플라본 관련 약물 흡수 영향",
    examples: ["귀리", "현미", "두부", "콩"],
    color: "bg-yellow-50 dark:bg-yellow-900/20 border-yellow-200 dark:border-yellow-800",
    iconBg: "bg-yellow-100 dark:bg-yellow-900/30",
  },
  {
    name: "견과류",
    icon: "🥜",
    description: "호두, 아몬드, 땅콩 등 미네랄·MAO 관련 약물 상호작용",
    examples: ["호두", "아몬드", "땅콩", "캐슈넛"],
    color: "bg-stone-50 dark:bg-stone-900/20 border-stone-200 dark:border-stone-800",
    iconBg: "bg-stone-100 dark:bg-stone-900/30",
  },
  {
    name: "해산물",
    icon: "🐟",
    description: "고등어, 미역 등 히스타민·요오드 관련 항히스타민제·갑상선약 상호작용",
    examples: ["고등어", "미역/다시마", "참치"],
    color: "bg-cyan-50 dark:bg-cyan-900/20 border-cyan-200 dark:border-cyan-800",
    iconBg: "bg-cyan-100 dark:bg-cyan-900/30",
  },
  {
    name: "육류",
    icon: "🥩",
    description: "소간, 숯불구이, 가공육 등 비타민A·티라민·CYP 유도 관련 상호작용",
    examples: ["소간", "숯불구이", "가공육"],
    color: "bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800",
    iconBg: "bg-red-100 dark:bg-red-900/30",
  },
  {
    name: "조미료/향신료",
    icon: "🧄",
    description: "마늘, 생강, 강황, 감초 등 항혈소판·CYP 억제 관련 상호작용",
    examples: ["마늘", "생강", "강황", "감초"],
    color: "bg-lime-50 dark:bg-lime-900/20 border-lime-200 dark:border-lime-800",
    iconBg: "bg-lime-100 dark:bg-lime-900/30",
  },
  {
    name: "발효식품",
    icon: "🫙",
    description: "간장, 된장, 김치, 낫토 등 티라민·비타민K2 관련 MAO·항응고제 상호작용",
    examples: ["간장", "된장", "김치", "낫토"],
    color: "bg-purple-50 dark:bg-purple-900/20 border-purple-200 dark:border-purple-800",
    iconBg: "bg-purple-100 dark:bg-purple-900/30",
  },
];

export default async function FoodsIndexPage() {
  let totalCount = 0;
  try {
    totalCount = await getFoodCount();
  } catch {
    /* 빌드 시 API 미연결 대비 */
  }

  return (
    <>
      <Breadcrumbs
        items={[
          { label: "홈", href: "/" },
          { label: "식품 목록" },
        ]}
      />

      <section className="max-w-3xl mx-auto px-4 py-6">
        <h1 className="text-2xl font-bold text-[var(--color-primary)] mb-2">
          식품 목록
        </h1>
        <p className="text-gray-500 dark:text-gray-400 mb-6">
          {totalCount > 0
            ? `약물과 상호작용이 알려진 ${totalCount}종의 식품을 카테고리별로 확인하세요.`
            : "약물과 상호작용이 알려진 주요 식품을 카테고리별로 확인하세요."}
          {" "}복약 시 주의해야 할 식품 정보를 제공합니다.
        </p>

        {/* 카테고리 그리드 */}
        <div className="grid gap-3 sm:gap-4 grid-cols-1 sm:grid-cols-2">
          {FOOD_CATEGORIES.map((cat) => (
            <div
              key={cat.name}
              className={`rounded-xl border p-4 shadow-sm ${cat.color}`}
            >
              <div className="flex items-start gap-3">
                <div className={`w-10 h-10 rounded-lg ${cat.iconBg} flex items-center justify-center text-lg shrink-0`}>
                  {cat.icon}
                </div>
                <div className="min-w-0">
                  <h2 className="font-semibold text-gray-900 dark:text-gray-100 mb-0.5">
                    {cat.name}
                  </h2>
                  <p className="text-xs text-gray-500 dark:text-gray-400 mb-2 line-clamp-2">
                    {cat.description}
                  </p>
                  <div className="flex flex-wrap gap-1">
                    {cat.examples.map((ex) => (
                      <span
                        key={ex}
                        className="inline-block px-2 py-0.5 text-[11px] rounded-full bg-white/70 dark:bg-gray-800/70 text-gray-600 dark:text-gray-300"
                      >
                        {ex}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>

        <AdBanner slot="foods-index-bottom" format="auto" className="mt-8" />

        {/* 면책조항 */}
        <p className="mt-6 text-xs text-gray-400 dark:text-gray-500 text-center">
          본 정보는 참고용이며, 의사/약사의 전문적 판단을 대체하지 않습니다.
        </p>
      </section>
    </>
  );
}
