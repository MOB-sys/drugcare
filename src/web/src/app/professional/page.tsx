/** 전문가용 약물 정보 랜딩 페이지 (SSG). */

import type { Metadata } from "next";
import Link from "next/link";
import { ProSearch } from "@/components/professional/ProSearch";

export const metadata: Metadata = {
  title: "의료 전문가용 약물 정보 | 약잘알",
  description:
    "의사, 약사, 간호사를 위한 상세 약물 정보를 제공합니다. 성분, DUR 안전성, 상호작용 정보를 밀도 높은 형태로 확인하세요.",
  openGraph: {
    title: "의료 전문가용 약물 정보 | 약잘알",
    description:
      "의사, 약사, 간호사를 위한 상세 약물 정보를 제공합니다.",
  },
};

const DRUG_CATEGORIES: { classNo: string; label: string }[] = [
  { classNo: "01", label: "신경계 약물" },
  { classNo: "02", label: "개개의 기관계 약물" },
  { classNo: "03", label: "대사성 약물" },
  { classNo: "04", label: "조직세포 기능 약물" },
  { classNo: "06", label: "항병원생물성 약물" },
  { classNo: "07", label: "치과/구강용 약물" },
  { classNo: "08", label: "생물학적 제제" },
  { classNo: "11", label: "해독제" },
  { classNo: "12", label: "진단용 약물" },
  { classNo: "13", label: "기타 약물" },
];

export default function ProfessionalPage() {
  const jsonLd = {
    "@context": "https://schema.org",
    "@type": "MedicalWebPage",
    name: "의료 전문가용 약물 정보",
    description:
      "의사, 약사, 간호사를 위한 상세 약물 정보를 제공합니다.",
    audience: {
      "@type": "MedicalAudience",
      audienceType: "MedicalProfessional",
    },
  };

  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd).replace(/</g, '\\u003c') }}
      />

      <div className="max-w-4xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-2">
            의료 전문가용 약물 정보
          </h1>
          <p className="text-sm text-gray-600 dark:text-gray-400">
            의사, 약사, 간호사를 위한 상세 약물 정보를 제공합니다.
            성분, DUR 안전성, 상호작용 정보를 밀도 높은 형태로 확인하세요.
          </p>
        </div>

        {/* Search */}
        <div className="mb-8">
          <ProSearch />
        </div>

        {/* Drug categories by class_no */}
        <section className="mb-8">
          <h2 className="text-sm font-semibold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-3">
            약효 분류별 탐색
          </h2>
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-2">
            {DRUG_CATEGORIES.map((cat) => (
              <Link
                key={cat.classNo}
                href={`/drugs?letter=${cat.classNo}`}
                className="px-3 py-2 text-xs font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-md hover:border-gray-400 dark:hover:border-gray-500 hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
              >
                <span className="text-gray-400 dark:text-gray-500 mr-1">[{cat.classNo}]</span>
                {cat.label}
              </Link>
            ))}
          </div>
        </section>

        {/* Quick links */}
        <section className="mb-8">
          <h2 className="text-sm font-semibold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-3">
            바로가기
          </h2>
          <div className="flex flex-wrap gap-2">
            <Link
              href="/check"
              className="px-3 py-2 text-xs font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-md hover:border-gray-400 dark:hover:border-gray-500 transition-colors"
            >
              상호작용 체크
            </Link>
            <Link
              href="/drugs"
              className="px-3 py-2 text-xs font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-md hover:border-gray-400 dark:hover:border-gray-500 transition-colors"
            >
              의약품 전체 목록
            </Link>
            <Link
              href="/supplements"
              className="px-3 py-2 text-xs font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-md hover:border-gray-400 dark:hover:border-gray-500 transition-colors"
            >
              건강기능식품 목록
            </Link>
          </div>
        </section>

        {/* Disclaimer */}
        <div className="border-t border-gray-200 dark:border-gray-700 pt-4">
          <p className="text-[11px] text-gray-400 dark:text-gray-500 leading-relaxed">
            본 정보는 전문 의료인의 임상적 판단을 보조하기 위한 참고 자료입니다.
            식약처 공공데이터를 기반으로 하며, 의사/약사의 전문적 판단을 대체하지 않습니다.
          </p>
        </div>
      </div>
    </>
  );
}
