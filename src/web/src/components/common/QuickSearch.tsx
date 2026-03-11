"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { searchDrugs } from "@/lib/api/drugs";
import { searchSupplements } from "@/lib/api/supplements";
import { searchFoods } from "@/lib/api/foods";
import { searchHerbalMedicines } from "@/lib/api/herbal";
import { useDebounce } from "@/lib/hooks/useDebounce";

interface QuickSearchProps {
  type: "drug" | "supplement" | "food" | "herbal";
  placeholder?: string;
}

interface SearchItem {
  slug: string;
  name: string;
  sub: string | null;
}

export function QuickSearch({ type, placeholder }: QuickSearchProps) {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<SearchItem[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const debouncedQuery = useDebounce(query, 300);

  useEffect(() => {
    const q = debouncedQuery.trim();
    if (q.length < 1) {
      setResults([]);
      return;
    }
    const controller = new AbortController();
    setIsLoading(true);

    (async () => {
      try {
        if (type === "drug") {
          const res = await searchDrugs(q, 1, 8);
          if (!controller.signal.aborted) setResults(res.items.map((d) => ({ slug: d.slug, name: d.item_name, sub: d.entp_name ?? null })));
        } else if (type === "supplement") {
          const res = await searchSupplements(q, 1, 8);
          if (!controller.signal.aborted) setResults(res.items.map((s) => ({ slug: s.slug, name: s.product_name, sub: s.company ?? null })));
        } else if (type === "food") {
          const res = await searchFoods(q, 1, 8);
          if (!controller.signal.aborted) setResults(res.items.map((f) => ({ slug: f.slug, name: f.name, sub: f.category ?? null })));
        } else {
          const res = await searchHerbalMedicines(q, 1, 8);
          if (!controller.signal.aborted) setResults(res.items.map((h) => ({ slug: h.slug, name: h.name, sub: h.korean_name ?? null })));
        }
      } catch {
        if (!controller.signal.aborted) setResults([]);
      } finally {
        if (!controller.signal.aborted) setIsLoading(false);
      }
    })();

    return () => controller.abort();
  }, [debouncedQuery, type]);

  const basePathMap: Record<string, string> = { drug: "/drugs", supplement: "/supplements", food: "/foods", herbal: "/herbal-medicines" };
  const basePath = basePathMap[type] ?? "/drugs";
  const placeholderMap: Record<string, string> = {
    drug: "의약품 이름으로 검색 (예: 타이레놀)",
    supplement: "건강기능식품 이름으로 검색 (예: 비타민D)",
    food: "식품 이름으로 검색 (예: 자몽)",
    herbal: "한약재 이름으로 검색 (예: 인삼)",
  };
  const defaultPlaceholder = placeholderMap[type] ?? "검색어를 입력하세요";

  return (
    <div className="mb-8">
      <div className="relative">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          maxLength={200}
          placeholder={placeholder || defaultPlaceholder}
          aria-label="검색어 입력"
          className="w-full px-4 py-3 pl-10 border border-gray-300 dark:border-gray-600 rounded-xl bg-[var(--color-surface)] text-[var(--color-text)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)] focus:border-transparent text-sm"
        />
        <svg className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400 dark:text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
        </svg>
        {isLoading && (
          <div className="absolute right-3 top-1/2 -translate-y-1/2">
            <div className="w-4 h-4 border-2 border-gray-300 dark:border-gray-600 border-t-[var(--color-primary)] rounded-full animate-spin" />
          </div>
        )}
      </div>

      {/* 검색 결과 드롭다운 */}
      {query.trim().length > 0 && results.length > 0 && (
        <ul className="mt-1 border border-gray-200 dark:border-gray-700 rounded-xl bg-[var(--color-surface)] shadow-lg overflow-hidden divide-y divide-gray-100 dark:divide-gray-700">
          {results.map((item) => (
            <li key={item.slug}>
              <Link
                href={`${basePath}/${item.slug}`}
                className="block px-4 py-3 hover:bg-[var(--color-primary-50)] dark:hover:bg-gray-800 transition-colors"
                onClick={() => { setQuery(""); setResults([]); }}
              >
                <p className="text-sm font-medium text-[var(--color-text)] truncate">{item.name}</p>
                {item.sub && <p className="text-xs text-[var(--color-text-muted)] mt-0.5 truncate">{item.sub}</p>}
              </Link>
            </li>
          ))}
        </ul>
      )}

      {query.trim().length > 0 && !isLoading && results.length === 0 && debouncedQuery === query && (
        <p className="mt-2 text-xs text-gray-400 dark:text-gray-500 text-center">검색 결과가 없습니다.</p>
      )}
    </div>
  );
}
