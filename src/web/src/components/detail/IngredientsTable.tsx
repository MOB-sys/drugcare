/** 성분 테이블 컴포넌트. */

import type { IngredientInfo } from "@/types/drug";

interface IngredientsTableProps {
  ingredients: IngredientInfo[];
}

export function IngredientsTable({ ingredients }: IngredientsTableProps) {
  if (ingredients.length === 0) return null;

  return (
    <section className="py-4 border-b border-gray-100 last:border-b-0">
      <h2 className="text-lg font-semibold text-gray-900 mb-3">성분 정보</h2>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-gray-200 text-left">
              <th className="py-2 pr-4 font-medium text-gray-600">성분명</th>
              <th className="py-2 pr-4 font-medium text-gray-600">함량</th>
              <th className="py-2 font-medium text-gray-600">단위</th>
            </tr>
          </thead>
          <tbody>
            {ingredients.map((ing, i) => (
              <tr key={i} className="border-b border-gray-50">
                <td className="py-2 pr-4 text-gray-900">{ing.name}</td>
                <td className="py-2 pr-4 text-gray-700">{ing.amount ?? "-"}</td>
                <td className="py-2 text-gray-700">{ing.unit ?? "-"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
