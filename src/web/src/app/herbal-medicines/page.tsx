import type { Metadata } from "next";
import { Breadcrumbs } from "@/components/common/Breadcrumbs";
import { AdBanner } from "@/components/ads/AdBanner";
import { getHerbalMedicineCount } from "@/lib/api/herbal";

export const metadata: Metadata = {
  title: "한약재 목록 — 대한약전 기반 생약 정보",
  description:
    "대한약전 기반 주요 한약재를 분류별로 찾아보세요. 인삼, 당귀, 황기 등 한약재의 효능, 주의사항, 약물 상호작용 정보를 확인할 수 있습니다.",
  openGraph: {
    title: "한약재 목록 — 약잘알",
    description: "대한약전 기반 한약재 분류별 인덱스",
    type: "website",
  },
};

export const revalidate = 86400;

/** 한약재 분류 정적 데이터 — seed_herbal_medicines.py 기반. */
const HERBAL_CATEGORIES = [
  {
    name: "보기약",
    description: "기(氣)를 보하는 약재. 비폐 기능 강화, 피로 개선",
    examples: ["인삼", "홍삼", "황기", "감초"],
    color: "bg-amber-50 dark:bg-amber-900/20 border-amber-200 dark:border-amber-800",
    iconBg: "bg-amber-100 dark:bg-amber-900/30",
    icon: "💛",
  },
  {
    name: "보혈약",
    description: "혈(血)을 보하는 약재. 빈혈 개선, 혈액순환",
    examples: ["당귀", "숙지황", "백작약", "하수오"],
    color: "bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800",
    iconBg: "bg-red-100 dark:bg-red-900/30",
    icon: "❤️",
  },
  {
    name: "보음약",
    description: "음(陰)을 자양하는 약재. 진액 생성, 자음윤조",
    examples: ["맥문동", "구기자", "석곡", "백합"],
    color: "bg-blue-50 dark:bg-blue-900/20 border-blue-200 dark:border-blue-800",
    iconBg: "bg-blue-100 dark:bg-blue-900/30",
    icon: "💧",
  },
  {
    name: "보양약",
    description: "양(陽)을 보하는 약재. 신양 보강, 근골 강화",
    examples: ["녹용", "음양곽", "두충", "육종용"],
    color: "bg-orange-50 dark:bg-orange-900/20 border-orange-200 dark:border-orange-800",
    iconBg: "bg-orange-100 dark:bg-orange-900/30",
    icon: "🔥",
  },
  {
    name: "해표약",
    description: "체표의 사기를 발산하는 약재. 감기, 발한, 해열",
    examples: ["마황", "계지", "갈근", "시호"],
    color: "bg-sky-50 dark:bg-sky-900/20 border-sky-200 dark:border-sky-800",
    iconBg: "bg-sky-100 dark:bg-sky-900/30",
    icon: "💨",
  },
  {
    name: "청열약",
    description: "열(熱)을 식히고 해독하는 약재. 소염, 항균",
    examples: ["황금", "황련", "금은화", "대황"],
    color: "bg-teal-50 dark:bg-teal-900/20 border-teal-200 dark:border-teal-800",
    iconBg: "bg-teal-100 dark:bg-teal-900/30",
    icon: "🧊",
  },
  {
    name: "거풍습약",
    description: "풍습을 제거하는 약재. 관절통, 근골통 완화",
    examples: ["독활", "천마", "오가피", "위령선"],
    color: "bg-emerald-50 dark:bg-emerald-900/20 border-emerald-200 dark:border-emerald-800",
    iconBg: "bg-emerald-100 dark:bg-emerald-900/30",
    icon: "🌿",
  },
  {
    name: "이수삼습약",
    description: "수습을 제거하고 이뇨하는 약재. 부종, 소변불리",
    examples: ["복령", "택사", "차전자", "의이인"],
    color: "bg-cyan-50 dark:bg-cyan-900/20 border-cyan-200 dark:border-cyan-800",
    iconBg: "bg-cyan-100 dark:bg-cyan-900/30",
    icon: "💦",
  },
  {
    name: "활혈거어약",
    description: "혈액순환을 촉진하고 어혈을 제거하는 약재",
    examples: ["단삼", "천궁", "은행잎", "홍화"],
    color: "bg-rose-50 dark:bg-rose-900/20 border-rose-200 dark:border-rose-800",
    iconBg: "bg-rose-100 dark:bg-rose-900/30",
    icon: "🩸",
  },
  {
    name: "지혈약",
    description: "출혈을 멎게 하는 약재",
    examples: ["삼칠근", "지유", "애엽"],
    color: "bg-pink-50 dark:bg-pink-900/20 border-pink-200 dark:border-pink-800",
    iconBg: "bg-pink-100 dark:bg-pink-900/30",
    icon: "🩹",
  },
  {
    name: "안신약",
    description: "마음을 안정시키고 수면을 돕는 약재. 불면, 불안",
    examples: ["산조인", "원지", "백자인"],
    color: "bg-indigo-50 dark:bg-indigo-900/20 border-indigo-200 dark:border-indigo-800",
    iconBg: "bg-indigo-100 dark:bg-indigo-900/30",
    icon: "🌙",
  },
  {
    name: "기타",
    description: "이기, 화담, 온리 등 다양한 기능의 한약재",
    examples: ["진피", "반하", "부자", "길경"],
    color: "bg-gray-50 dark:bg-gray-800/50 border-gray-200 dark:border-gray-700",
    iconBg: "bg-gray-100 dark:bg-gray-800",
    icon: "🌱",
  },
];

export default async function HerbalMedicinesIndexPage() {
  let totalCount = 0;
  try {
    totalCount = await getHerbalMedicineCount();
  } catch {
    /* 빌드 시 API 미연결 대비 */
  }

  return (
    <>
      <Breadcrumbs
        items={[
          { label: "홈", href: "/" },
          { label: "한약재 목록" },
        ]}
      />

      <section className="max-w-3xl mx-auto px-4 py-6">
        <h1 className="text-2xl font-bold text-[var(--color-primary)] mb-2">
          한약재 목록
        </h1>
        <p className="text-gray-500 dark:text-gray-400 mb-6">
          {totalCount > 0
            ? `대한약전 기반 ${totalCount}종의 한약재를 분류별로 확인하세요.`
            : "대한약전 기반 주요 한약재를 분류별로 확인하세요."}
          {" "}효능, 주의사항, 약물 상호작용 정보를 제공합니다.
        </p>

        {/* 카테고리 그리드 */}
        <div className="grid gap-3 sm:gap-4 grid-cols-1 sm:grid-cols-2">
          {HERBAL_CATEGORIES.map((cat) => (
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

        <AdBanner slot="herbal-index-bottom" format="auto" className="mt-8" />

        {/* 면책조항 */}
        <p className="mt-6 text-xs text-gray-400 dark:text-gray-500 text-center">
          본 정보는 참고용이며, 의사/약사의 전문적 판단을 대체하지 않습니다.
          한약재는 반드시 전문가의 처방에 따라 복용하세요.
        </p>
      </section>
    </>
  );
}
