import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "약물 비교",
  description: "두 가지 약물 또는 건강기능식품의 효능, 성분, 부작용을 한눈에 비교하세요.",
  openGraph: {
    title: "약물 비교 — 약잘알",
    description: "두 가지 약물 또는 건강기능식품의 효능, 성분, 부작용을 한눈에 비교하세요.",
  },
};

export default function CompareLayout({ children }: { children: React.ReactNode }) {
  return children;
}
