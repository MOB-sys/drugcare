import React from "react";
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

const CATEGORY_ICONS: Record<string, React.ReactNode> = {
  fruit: <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 2C9 2 7 4 7 7c0 4 5 7 5 7s5-3 5-7c0-3-2-5-5-5z" /><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 2c1-1 3-1 4 0" /></svg>,
  dairy: <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M8 2h8l1 5v13a2 2 0 01-2 2H9a2 2 0 01-2-2V7l1-5z" /><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M8 7h8" /></svg>,
  beverage: <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M18 8h1a4 4 0 010 8h-1M5 8h12v9a4 4 0 01-4 4H9a4 4 0 01-4-4V8zM7 2v3M12 2v3M17 2v3" /></svg>,
  alcohol: <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 2l3 7m0 0l3-7m-3 7v13m-4 0h8" /></svg>,
  meal: <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M3 13h18M5 17h14a2 2 0 002-2v-1H3v1a2 2 0 002 2zM12 3C7 3 3 7 3 12h18c0-5-4-9-9-9z" /></svg>,
  other: <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>,
};

/** Single food interaction card. */
function FoodCard({ item }: { item: FoodInteraction }) {
  const colorClass = CATEGORY_COLORS[item.food.category] ?? CATEGORY_COLORS.other;
  const icon = CATEGORY_ICONS[item.food.category] ?? CATEGORY_ICONS.other;

  return (
    <div className={`rounded-lg border p-3 ${colorClass}`}>
      <div className="flex items-center gap-2 mb-1.5">
        <span className="text-gray-600 shrink-0" aria-label={item.food.name}>
          {icon}
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
