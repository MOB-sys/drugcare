import type { Metadata } from "next";
import { Breadcrumbs } from "@/components/common/Breadcrumbs";
import { AdBanner } from "@/components/ads/AdBanner";
import { SymptomChecker } from "./SymptomChecker";

export const metadata: Metadata = {
  title: "증상별 약물 검색 | PillRight",
  description:
    "두통, 소화불량, 기침 등 증상에 맞는 의약품을 검색하세요. 증상별로 효능이 있는 약물을 빠르게 찾을 수 있습니다.",
  openGraph: {
    title: "증상별 약물 검색 | PillRight",
    description:
      "증상에 맞는 의약품을 빠르게 검색하세요.",
  },
};

export default function SymptomsPage() {
  return (
    <>
      <Breadcrumbs
        items={[
          { label: "홈", href: "/" },
          { label: "증상별 약물 검색" },
        ]}
      />

      <div className="max-w-5xl mx-auto px-4 py-8">
        {/* 히어로 */}
        <section className="text-center mb-10">
          <h1 className="text-3xl font-bold text-[var(--color-primary)] mb-3">
            어떤 증상이 있으신가요?
          </h1>
          <p className="text-gray-500 max-w-lg mx-auto">
            증상을 선택하거나 직접 입력하면, 해당 증상에 효능이 있는 의약품을 찾아드립니다.
          </p>
        </section>

        <SymptomChecker />

        <AdBanner slot="symptoms-bottom" format="horizontal" />

        {/* 면책조항 */}
        <div className="mt-8 p-4 bg-amber-50 border border-amber-200 rounded-xl">
          <p className="text-sm text-amber-800 font-medium mb-1">
            주의사항
          </p>
          <p className="text-xs text-amber-700">
            이 서비스는 자가 진단 도구가 아닙니다. 검색 결과는 식약처 공공데이터의 효능효과 정보를 기반으로 하며,
            의사/약사의 전문적 판단을 대체하지 않습니다. 증상이 지속되면 반드시 의사와 상담하세요.
          </p>
        </div>
      </div>
    </>
  );
}
