/**
 * 매칭된 성분 가이드 카드 표시.
 * IngredientsTable 아래에 배치하여 성분별 요약·팁·링크를 제공합니다.
 */

import Link from "next/link";
import type { MatchedIngredient } from "@/lib/utils/ingredientMatcher";
import { categoryConfig } from "@/lib/data/ingredients";

interface IngredientGuideSectionProps {
  matchedIngredients: MatchedIngredient[];
}

export function IngredientGuideSection({
  matchedIngredients,
}: IngredientGuideSectionProps) {
  if (matchedIngredients.length === 0) return null;

  return (
    <section className="py-4 border-b border-gray-100 dark:border-gray-700 last:border-b-0 scroll-mt-24">
      <h3 className="text-base font-semibold text-gray-800 dark:text-gray-200 mb-3">
        주요 성분 가이드
      </h3>
      <div className="space-y-3">
        {matchedIngredients.slice(0, 4).map(({ guide }) => {
          const config = categoryConfig[guide.category];
          return (
            <Link
              key={guide.slug}
              href={`/ingredients/${guide.slug}`}
              className="block rounded-lg border border-gray-200 dark:border-gray-700 hover:border-[var(--color-primary-100)] hover:shadow-sm transition-all p-4"
            >
              <div className="flex items-center gap-2 mb-1.5">
                <span className="text-sm font-semibold text-gray-900 dark:text-gray-100">
                  {guide.name}
                </span>
                <span
                  className={`px-1.5 py-0.5 rounded text-xs font-medium ${config.bgClass} ${config.textClass}`}
                >
                  {config.label}
                </span>
              </div>
              <p className="text-sm text-gray-600 dark:text-gray-400 leading-relaxed line-clamp-2">
                {guide.summary}
              </p>
              {guide.tips.length > 0 && (
                <p className="text-xs text-[var(--color-primary)] mt-2">
                  TIP: {guide.tips[0]}
                </p>
              )}
            </Link>
          );
        })}
      </div>
    </section>
  );
}
