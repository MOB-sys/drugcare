/**
 * 약물 분류 정보 섹션.
 * 분류 설명 + 주의사항 + 대표 약물 태그 + 분류 상세 링크.
 */

import Link from "next/link";
import type { DrugCategory } from "@/lib/data/drugCategories";

interface CategoryInfoSectionProps {
  category: DrugCategory;
}

export function CategoryInfoSection({ category }: CategoryInfoSectionProps) {
  return (
    <section className="py-4 border-b border-gray-100 dark:border-gray-700 last:border-b-0 scroll-mt-24">
      <div className="rounded-lg bg-blue-50/50 dark:bg-blue-900/10 border border-blue-200/50 dark:border-blue-800/30 p-4">
        <div className="flex items-center justify-between mb-2">
          <h3 className="text-base font-semibold text-gray-800 dark:text-gray-200">
            {category.name} 분류 안내
          </h3>
          <Link
            href={`/categories/${category.slug}`}
            className="text-xs text-[var(--color-primary)] hover:underline shrink-0"
          >
            분류 상세 보기
          </Link>
        </div>
        <p className="text-sm text-gray-600 dark:text-gray-400 leading-relaxed mb-3">
          {category.description}
        </p>

        {category.precautions.length > 0 && (
          <div className="mb-3">
            <p className="text-xs font-semibold text-gray-500 dark:text-gray-400 mb-1">
              주요 주의사항
            </p>
            <ul className="text-xs text-gray-600 dark:text-gray-400 space-y-1">
              {category.precautions.slice(0, 3).map((p, i) => (
                <li key={i} className="flex gap-1.5">
                  <span className="text-amber-500 shrink-0">!</span>
                  <span>{p}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {category.examples.length > 0 && (
          <div>
            <p className="text-xs font-semibold text-gray-500 dark:text-gray-400 mb-1.5">
              같은 분류 대표 약물
            </p>
            <div className="flex flex-wrap gap-1.5">
              {category.examples.slice(0, 6).map((ex) => (
                <span
                  key={ex}
                  className="px-2 py-0.5 rounded-full text-xs bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300"
                >
                  {ex}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>
    </section>
  );
}
