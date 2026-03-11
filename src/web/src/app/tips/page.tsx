import type { Metadata } from "next";
import { tips } from "@/lib/data/tips";
import { Breadcrumbs } from "@/components/common/Breadcrumbs";
import { TipsList } from "@/components/tips/TipsList";
import { SITE_URL } from "@/lib/constants/site";

const siteUrl = SITE_URL;

export const metadata: Metadata = {
  title: "건강팁 — 약과 영양제, 똑똑하게 복용하기",
  description:
    "약물 상호작용, 영양제 복용법, 복약 타이밍 등 꼭 알아야 할 건강 정보를 쉽게 정리했습니다.",
  openGraph: {
    title: "건강팁 — 약잘알",
    description: "약과 영양제, 똑똑하게 복용하는 방법",
    type: "website",
    images: [
      {
        url: `${siteUrl}/api/og?title=${encodeURIComponent("건강팁 — 약과 영양제, 똑똑하게 복용하기")}&type=tip`,
        width: 1200,
        height: 630,
        alt: "건강팁 — 약잘알",
      },
    ],
  },
};

export default function TipsPage() {
  return (
    <>
      <Breadcrumbs
        items={[
          { label: "홈", href: "/" },
          { label: "건강팁" },
        ]}
      />

      <section className="max-w-3xl mx-auto px-4 py-6">
        <h1 className="text-2xl font-bold text-[var(--color-primary)] mb-2">건강팁</h1>
        <p className="text-gray-500 dark:text-gray-400 mb-6">
          약과 영양제를 안전하고 효과적으로 복용하기 위한 정보를 모았습니다.
        </p>

        <TipsList tips={tips} />
      </section>
    </>
  );
}
