/** 전문가용 약물 상세 페이지 (SSG). */

import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { getDrugBySlug, getAllDrugSlugs } from "@/lib/api/drugs";
import { ProDrugHeader } from "@/components/professional/ProDrugHeader";
import { ProDrugTabs } from "@/components/professional/ProDrugTabs";

interface PageProps {
  params: Promise<{ slug: string }>;
}

/* -- SSG -------------------------------------------------- */

export async function generateStaticParams() {
  try {
    const slugs = await getAllDrugSlugs();
    return slugs.map((slug) => ({ slug }));
  } catch {
    return [];
  }
}

export async function generateMetadata({ params }: PageProps): Promise<Metadata> {
  const { slug } = await params;
  try {
    const drug = await getDrugBySlug(slug);
    const title = `${drug.item_name} - 전문가 약물정보 | 약잘알`;
    const desc = [
      drug.item_seq && `품목기준코드 ${drug.item_seq}`,
      drug.entp_name,
      drug.etc_otc_code,
    ]
      .filter(Boolean)
      .join(" | ");

    return {
      title,
      description: desc || `${drug.item_name} 전문가용 약물 상세 정보`,
      openGraph: { title, description: desc },
    };
  } catch {
    return { title: "전문가 약물정보 | 약잘알" };
  }
}

/* -- Page ------------------------------------------------- */

export default async function ProDrugDetailPage({ params }: PageProps) {
  const { slug } = await params;
  let drug;
  try {
    drug = await getDrugBySlug(slug);
  } catch {
    notFound();
  }

  const jsonLd = {
    "@context": "https://schema.org",
    "@type": "MedicalWebPage",
    name: `${drug.item_name} - 전문가용 약물 정보`,
    about: {
      "@type": "Drug",
      name: drug.item_name,
      manufacturer: drug.entp_name
        ? { "@type": "Organization", name: drug.entp_name }
        : undefined,
    },
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

      <div className="max-w-4xl mx-auto px-4 py-6">
        {/* Breadcrumb */}
        <nav className="text-[11px] text-gray-400 dark:text-gray-500 mb-4 flex items-center gap-1">
          <Link href="/professional" className="hover:text-gray-600 dark:hover:text-gray-300">
            전문가
          </Link>
          <span>/</span>
          <span className="text-gray-600 dark:text-gray-400 truncate max-w-xs">
            {drug.item_name}
          </span>
        </nav>

        {/* Header */}
        <div className="mb-4">
          <ProDrugHeader drug={drug} />
        </div>

        {/* Tabs */}
        <div className="mb-6">
          <ProDrugTabs drug={drug} />
        </div>

        {/* Cross links */}
        <div className="flex flex-wrap gap-3 text-xs mb-6">
          <Link
            href={`/drugs/${slug}`}
            className="text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300 underline underline-offset-2"
          >
            일반 사용자용 페이지로 보기
          </Link>
          <Link
            href="/check"
            className="text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300 underline underline-offset-2"
          >
            상호작용 체크
          </Link>
          <Link
            href="/professional"
            className="text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300 underline underline-offset-2"
          >
            전문가 메인
          </Link>
        </div>

        {/* Disclaimer */}
        <p className="text-[11px] text-gray-400 dark:text-gray-500 border-t border-gray-200 dark:border-gray-700 pt-3">
          본 정보는 전문 의료인의 임상적 판단을 보조하기 위한 참고 자료입니다.
          식약처 공공데이터를 기반으로 하며, 의사/약사의 전문적 판단을 대체하지 않습니다.
        </p>
      </div>
    </>
  );
}
