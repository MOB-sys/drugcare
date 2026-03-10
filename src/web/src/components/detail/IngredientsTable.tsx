/** 성분 테이블 컴포넌트. */

import type { IngredientInfo } from "@/types/drug";

interface IngredientsTableProps {
  ingredients: IngredientInfo[];
}

export function IngredientsTable({ ingredients }: IngredientsTableProps) {
  if (ingredients.length === 0) return null;

  return (
    <section className="py-4 border-b border-gray-100 dark:border-gray-700 last:border-b-0">
      <h2 className="text-lg font-semibold text-[var(--color-primary)] mb-3">성분 정보</h2>
      <div className="overflow-x-auto rounded-lg border border-gray-200 dark:border-gray-700">
        <table className="w-full text-sm">
          <thead>
            <tr className="bg-[var(--color-primary-50)] text-left">
              <th className="py-2.5 px-4 font-medium text-[var(--color-primary)] text-xs uppercase tracking-wider">성분명</th>
              <th className="py-2.5 px-4 font-medium text-[var(--color-primary)] text-xs uppercase tracking-wider">함량</th>
              <th className="py-2.5 px-4 font-medium text-[var(--color-primary)] text-xs uppercase tracking-wider">단위</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100 dark:divide-gray-700">
            {ingredients.map((ing, i) => (
              <tr key={i} className="hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors">
                <td className="py-2.5 px-4 text-gray-900 dark:text-gray-100">{ing.name}</td>
                <td className="py-2.5 px-4 text-gray-700 dark:text-gray-300">{ing.amount ?? "-"}</td>
                <td className="py-2.5 px-4 text-gray-700 dark:text-gray-300">{ing.unit ?? "-"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
