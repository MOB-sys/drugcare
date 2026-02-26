import type { Metadata } from "next";
import Link from "next/link";
import { tips } from "@/lib/data/tips";

export const metadata: Metadata = {
  title: "건강팁 — 약과 영양제, 똑똑하게 복용하기",
  description:
    "약물 상호작용, 영양제 복용법, 복약 타이밍 등 꼭 알아야 할 건강 정보를 쉽게 정리했습니다.",
  openGraph: {
    title: "건강팁 — 약먹어",
    description: "약과 영양제, 똑똑하게 복용하는 방법",
    type: "website",
  },
};

export default function TipsPage() {
  return (
    <section className="max-w-3xl mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold text-gray-900 mb-2">건강팁</h1>
      <p className="text-gray-500 mb-8">
        약과 영양제를 안전하고 효과적으로 복용하기 위한 정보를 모았습니다.
      </p>

      <div className="grid gap-4 sm:grid-cols-2">
        {tips.map((tip) => (
          <Link
            key={tip.slug}
            href={`/tips/${tip.slug}`}
            className="block bg-white rounded-xl border border-gray-200 p-5 hover:border-[var(--color-brand)] hover:shadow-sm transition-all"
          >
            <h2 className="text-lg font-semibold text-gray-900 mb-2 break-keep">
              {tip.title}
            </h2>
            <p className="text-sm text-gray-500 line-clamp-2">
              {tip.description}
            </p>
            <div className="flex flex-wrap gap-1.5 mt-3">
              {tip.tags.map((tag) => (
                <span
                  key={tag}
                  className="text-xs px-2 py-0.5 rounded-full bg-gray-100 text-gray-500"
                >
                  {tag}
                </span>
              ))}
            </div>
          </Link>
        ))}
      </div>
    </section>
  );
}
