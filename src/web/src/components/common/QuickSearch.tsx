"use client";

import { useState, useCallback, useEffect } from "react";
import Link from "next/link";
import { searchDrugs } from "@/lib/api/drugs";
import { searchSupplements } from "@/lib/api/supplements";
import { useDebounce } from "@/lib/hooks/useDebounce";

interface QuickSearchProps {
  type: "drug" | "supplement";
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

  const doSearch = useCallback(async (q: string) => {
    if (q.trim().length < 1) {
      setResults([]);
      return;
    }
    setIsLoading(true);
    try {
      if (type === "drug") {
        const res = await searchDrugs(q, 1, 8);
        setResults(res.items.map((d) => ({ slug: d.slug, name: d.item_name, sub: d.entp_name ?? null })));
      } else {
        const res = await searchSupplements(q, 1, 8);
        setResults(res.items.map((s) => ({ slug: s.slug, name: s.product_name, sub: s.company ?? null })));
      }
    } catch {
      setResults([]);
    } finally {
      setIsLoading(false);
    }
  }, [type]);

  useEffect(() => {
    doSearch(debouncedQuery);
  }, [debouncedQuery, doSearch]);

  const basePath = type === "drug" ? "/drugs" : "/supplements";
  const defaultPlaceholder = type === "drug" ? "의약품 이름으로 검색 (예: 타이레놀)" : "건강기능식품 이름으로 검색 (예: 비타민D)";

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
        <svg className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
        </svg>
        {isLoading && (
          <div className="absolute right-3 top-1/2 -translate-y-1/2">
            <div className="w-4 h-4 border-2 border-gray-300 border-t-[var(--color-primary)] rounded-full animate-spin" />
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
        <p className="mt-2 text-xs text-gray-400 text-center">검색 결과가 없습니다.</p>
      )}
    </div>
  );
}
