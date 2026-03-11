"use client";

import { useState, useMemo } from "react";
import Link from "next/link";
import type { FoodSearchItem } from "@/types/food";

interface CategoryMeta {
  icon: string;
  color: string;
}

interface FoodListClientProps {
  items: FoodSearchItem[];
  categories: string[];
  categoryMeta: Record<string, CategoryMeta>;
  defaultMeta: CategoryMeta;
}

export function FoodListClient({
  items,
  categories,
  categoryMeta,
  defaultMeta,
}: FoodListClientProps) {
  const [activeCategory, setActiveCategory] = useState<string | null>(null);
  const [search, setSearch] = useState("");

  const filtered = useMemo(() => {
    let result = items;
    if (activeCategory) {
      result = result.filter((item) => (item.category || "기타") === activeCategory);
    }
    if (search.trim()) {
      const q = search.trim().toLowerCase();
      result = result.filter((item) => item.name.toLowerCase().includes(q));
    }
    return result;
  }, [items, activeCategory, search]);

  const grouped = useMemo(() => {
    const map = new Map<string, FoodSearchItem[]>();
    for (const item of filtered) {
      const cat = item.category || "기타";
      if (!map.has(cat)) map.set(cat, []);
      map.get(cat)!.push(item);
    }
    return map;
  }, [filtered]);

  const getMeta = (cat: string) => categoryMeta[cat] || defaultMeta;

  return (
    <>
      {/* 검색 */}
      <div className="mb-4">
        <input
          type="text"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="식품명으로 검색..."
          className="w-full px-4 py-2.5 rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 text-sm focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]/30"
        />
      </div>

      {/* 카테고리 필터 칩 */}
      <div className="flex flex-wrap gap-2 mb-6">
        <button
          onClick={() => setActiveCategory(null)}
          className={`px-3 py-1.5 rounded-full text-sm font-medium transition-colors ${
            activeCategory === null
              ? "bg-[var(--color-primary)] text-white"
              : "bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-gray-700"
          }`}
        >
          전체 ({items.length})
        </button>
        {categories.map((cat) => {
          const meta = getMeta(cat);
          const count = items.filter((i) => (i.category || "기타") === cat).length;
          return (
            <button
              key={cat}
              onClick={() => setActiveCategory(activeCategory === cat ? null : cat)}
              className={`px-3 py-1.5 rounded-full text-sm font-medium transition-colors ${
                activeCategory === cat
                  ? "bg-[var(--color-primary)] text-white"
                  : `${meta.color} hover:opacity-80`
              }`}
            >
              {meta.icon} {cat} ({count})
            </button>
          );
        })}
      </div>

      {/* 결과 수 */}
      {(activeCategory || search.trim()) && (
        <p className="text-sm text-gray-500 dark:text-gray-400 mb-4">
          {filtered.length}건의 식품
        </p>
      )}

      {/* 카테고리별 아이템 목록 */}
      {filtered.length === 0 ? (
        <div className="text-center py-12 text-gray-400 dark:text-gray-500">
          <p className="text-lg mb-1">검색 결과가 없습니다</p>
          <p className="text-sm">다른 검색어나 카테고리를 선택해보세요.</p>
        </div>
      ) : (
        <div className="space-y-6">
          {Array.from(grouped.entries()).map(([cat, catItems]) => {
            const meta = getMeta(cat);
            return (
              <div key={cat}>
                <h2 className="flex items-center gap-2 text-lg font-semibold text-gray-900 dark:text-gray-100 mb-3">
                  <span className={`inline-flex items-center justify-center w-7 h-7 rounded-lg text-sm ${meta.color}`}>
                    {meta.icon}
                  </span>
                  {cat}
                  <span className="text-sm font-normal text-gray-400">({catItems.length})</span>
                </h2>
                <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-2">
                  {catItems.map((item) => (
                    <Link
                      key={item.id}
                      href={`/foods/${item.slug}`}
                      className="group flex items-center gap-2 px-3 py-2.5 rounded-lg border border-gray-100 dark:border-gray-700 bg-white dark:bg-gray-800 hover:border-[var(--color-primary)]/40 hover:shadow-sm transition-all"
                    >
                      <span className="text-sm text-gray-800 dark:text-gray-200 group-hover:text-[var(--color-primary)] transition-colors truncate">
                        {item.name}
                      </span>
                      <svg className="w-3.5 h-3.5 text-gray-300 dark:text-gray-600 group-hover:text-[var(--color-primary)] ml-auto shrink-0 transition-colors" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                        <path strokeLinecap="round" strokeLinejoin="round" d="M9 5l7 7-7 7" />
                      </svg>
                    </Link>
                  ))}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </>
  );
}
