import type { Metadata } from "next";
import { SITE_URL } from "@/lib/constants/site";

export const metadata: Metadata = {
  title: "약물 비교",
  description: "두 가지 약물 또는 건강기능식품의 효능, 성분, 부작용을 한눈에 비교하세요.",
  openGraph: {
    title: "약물 비교 — 약잘알",
    description: "두 가지 약물 또는 건강기능식품의 효능, 성분, 부작용을 한눈에 비교하세요.",
  },
};

const jsonLd = {
  "@context": "https://schema.org",
  "@type": "WebApplication",
  name: "약물 비교 — 약잘알",
  description: "두 가지 약물 또는 건강기능식품의 효능, 성분, 부작용을 한눈에 비교",
  url: `${SITE_URL}/compare`,
  applicationCategory: "HealthApplication",
  isPartOf: { "@type": "WebSite", name: "약잘알", url: SITE_URL },
};

export default function CompareLayout({ children }: { children: React.ReactNode }) {
  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
      />
      {children}
    </>
  );
}
