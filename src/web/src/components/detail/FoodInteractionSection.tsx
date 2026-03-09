import { parseFoodInteractions, type FoodInteraction } from "@/lib/utils/foodInteractionParser";

interface FoodInteractionSectionProps {
  intrcText: string | null;
}

const CATEGORY_COLORS: Record<string, string> = {
  fruit: "bg-orange-50 border-orange-200",
  dairy: "bg-blue-50 border-blue-200",
  beverage: "bg-amber-50 border-amber-200",
  alcohol: "bg-red-50 border-red-200",
  meal: "bg-emerald-50 border-emerald-200",
  other: "bg-gray-50 border-gray-200",
};

/** Single food interaction card. */
function FoodCard({ item }: { item: FoodInteraction }) {
  const colorClass = CATEGORY_COLORS[item.food.category] ?? CATEGORY_COLORS.other;

  return (
    <div className={`rounded-lg border p-3 ${colorClass}`}>
      <div className="flex items-center gap-2 mb-1.5">
        <span className="text-lg" role="img" aria-label={item.food.name}>
          {item.food.icon}
        </span>
        <div>
          <span className="font-semibold text-sm text-gray-900">{item.food.name}</span>
          <span className="text-xs text-gray-500 ml-1.5">{item.food.categoryLabel}</span>
        </div>
      </div>
      {item.contextText && (
        <p className="text-xs text-gray-600 leading-relaxed break-keep line-clamp-3">
          {item.contextText}
        </p>
      )}
    </div>
  );
}

/** Show detected food interactions as visual cards. */
export function FoodInteractionSection({ intrcText }: FoodInteractionSectionProps) {
  const interactions = parseFoodInteractions(intrcText);
  if (interactions.length === 0) return null;

  return (
    <section id="food-interactions" className="py-4 border-b border-gray-100 last:border-b-0 scroll-mt-24">
      <div className="flex items-center gap-2 mb-3">
        <svg className="w-5 h-5 text-[var(--color-primary)]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 100 4 2 2 0 000-4z" />
        </svg>
        <h2 className="text-lg font-semibold text-[var(--color-primary)]">음식 상호작용</h2>
        <span className="text-xs text-gray-400 ml-auto">{interactions.length}건 감지</span>
      </div>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
        {interactions.map((item, i) => (
          <FoodCard key={i} item={item} />
        ))}
      </div>
      <p className="text-xs text-gray-400 mt-2">
        자동 감지된 정보이며, 상세 내용은 상호작용 항목을 참고하세요.
      </p>
    </section>
  );
}
