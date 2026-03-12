"use client";

import { useState, useMemo } from "react";
import Link from "next/link";
import type { ContentTip } from "@/lib/content/types";
import { AdBanner } from "@/components/ads/AdBanner";

const CATEGORIES = [
  { key: "all", label: "전체" },
  { key: "약물 상호작용", label: "상호작용" },
  { key: "영양제", label: "영양제" },
  { key: "복약", label: "복약 가이드" },
  { key: "대상별", label: "대상별 주의" },
] as const;

function matchesCategory(tip: ContentTip, category: string): boolean {
  if (category === "all") return true;
  if (category === "약물 상호작용") {
    return tip.tags.some((t) => t.includes("상호작용") || t.includes("약 조합"));
  }
  if (category === "영양제") {
    return tip.tags.some((t) =>
      t.includes("영양제") || t.includes("비타민") || t.includes("오메가") ||
      t.includes("유산균") || t.includes("건강기능식품") || t.includes("프로바이오틱스"),
    );
  }
  if (category === "복약") {
    return tip.tags.some((t) =>
      t.includes("복용") || t.includes("복약") || t.includes("가이드") || t.includes("항생제"),
    );
  }
  if (category === "대상별") {
    return tip.tags.some((t) =>
      t.includes("임산부") || t.includes("어린이") || t.includes("고령자") ||
      t.includes("소아") || t.includes("나이대별"),
    );
  }
  return false;
}

export function TipsList({ tips }: { tips: ContentTip[] }) {
  const [category, setCategory] = useState("all");

  const filtered = useMemo(
    () => tips.filter((tip) => matchesCategory(tip, category)),
    [tips, category],
  );

  const midIndex = Math.ceil(filtered.length / 2);

  return (
    <>
      {/* 카테고리 필터 */}
      <div className="flex flex-wrap gap-2 mb-6">
        {CATEGORIES.map((cat) => (
          <button
            key={cat.key}
            onClick={() => setCategory(cat.key)}
            className={`px-3 py-1.5 rounded-full text-sm font-medium transition-all ${
              category === cat.key
                ? "bg-[var(--color-primary)] text-white shadow-sm"
                : "bg-[var(--color-primary-50)] text-[var(--color-primary)] hover:bg-[var(--color-primary-100)]"
            }`}
          >
            {cat.label}
          </button>
        ))}
      </div>

      {filtered.length === 0 ? (
        <div className="py-12 text-center text-gray-400 dark:text-gray-500">
          <p className="text-sm">해당 카테고리의 건강팁이 없습니다.</p>
        </div>
      ) : (
        <>
          <div className="grid gap-4 sm:grid-cols-2">
            {filtered.slice(0, midIndex).map((tip) => (
              <TipCard key={tip.slug} tip={tip} />
            ))}
          </div>

          <AdBanner slot="tips-list-mid" format="auto" className="my-6" />

          {filtered.length > midIndex && (
            <div className="grid gap-4 sm:grid-cols-2">
              {filtered.slice(midIndex).map((tip) => (
                <TipCard key={tip.slug} tip={tip} />
              ))}
            </div>
          )}
        </>
      )}
    </>
  );
}

function TipCard({ tip }: { tip: ContentTip }) {
  return (
    <Link
      href={`/tips/${tip.slug}`}
      className="group block bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-700 p-5 shadow-sm hover:shadow-md hover:border-[var(--color-primary-100)] transition-all"
    >
      <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-2 break-keep group-hover:text-[var(--color-primary)] transition-colors">
        {tip.title}
      </h2>
      <p className="text-sm text-gray-500 dark:text-gray-400 line-clamp-2">
        {tip.description}
      </p>
      <div className="flex flex-wrap gap-1.5 mt-3">
        {tip.tags.map((tag) => (
          <span
            key={tag}
            className="text-xs px-2 py-0.5 rounded-full bg-[var(--color-primary-50)] text-[var(--color-primary)]"
          >
            {tag}
          </span>
        ))}
      </div>
    </Link>
  );
}
