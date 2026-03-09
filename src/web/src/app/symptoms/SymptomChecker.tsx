"use client";

import { useState, useCallback, type ReactNode } from "react";
import Link from "next/link";
import { SYMPTOM_CATEGORIES } from "@/lib/data/symptoms";
import { searchDrugsBySymptom } from "@/lib/api/drugs";
import type { DrugSearchItem } from "@/types/drug";

const CATEGORY_ICONS: Record<string, ReactNode> = {
  pain: (
    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M13 10V3L4 14h7v7l9-11h-7z" />
    </svg>
  ),
  digestive: (
    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
    </svg>
  ),
  respiratory: (
    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M3 15a4 4 0 004 4h9a5 5 0 10-.1-9.999 5.002 5.002 0 10-9.78 2.096A4.001 4.001 0 003 15z" />
    </svg>
  ),
  skin: (
    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M7 21a4 4 0 01-4-4V5a2 2 0 012-2h4a2 2 0 012 2v12a4 4 0 01-4 4zm0 0h12a2 2 0 002-2v-4a2 2 0 00-2-2h-2.343M11 7.343l1.657-1.657a2 2 0 012.828 0l2.829 2.829a2 2 0 010 2.828l-8.486 8.485M7 17h.01" />
    </svg>
  ),
  other: (
    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
    </svg>
  ),
};

/** 증상 체커 클라이언트 컴포넌트. */
export function SymptomChecker() {
  const [expandedCat, setExpandedCat] = useState<string | null>(null);
  const [selectedSymptom, setSelectedSymptom] = useState<string>("");
  const [customQuery, setCustomQuery] = useState("");
  const [results, setResults] = useState<DrugSearchItem[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(0);
  const [loading, setLoading] = useState(false);
  const [searched, setSearched] = useState(false);

  const doSearch = useCallback(async (q: string, p: number) => {
    if (!q.trim()) return;
    setLoading(true);
    setSearched(true);
    try {
      const res = await searchDrugsBySymptom(q, p, 20);
      setResults(res.items);
      setTotal(res.total);
      setPage(res.page);
      setTotalPages(Math.ceil(res.total / 20));
    } catch {
      setResults([]);
      setTotal(0);
    } finally {
      setLoading(false);
    }
  }, []);

  const handleSymptomClick = (symptom: string) => {
    setSelectedSymptom(symptom);
    setCustomQuery(symptom);
    doSearch(symptom, 1);
  };

  const handleCustomSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (customQuery.trim()) {
      setSelectedSymptom(customQuery.trim());
      doSearch(customQuery.trim(), 1);
    }
  };

  const handlePageChange = (newPage: number) => {
    doSearch(selectedSymptom, newPage);
  };

  return (
    <div className="space-y-8">
      {/* 커스텀 검색 */}
      <form onSubmit={handleCustomSearch} className="flex gap-2 max-w-lg mx-auto">
        <input
          type="text"
          value={customQuery}
          onChange={(e) => setCustomQuery(e.target.value)}
          placeholder="증상을 직접 입력하세요 (예: 두통, 소화불량)"
          className="flex-1 px-4 py-2.5 border border-gray-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]/30 focus:border-[var(--color-primary)]"
        />
        <button
          type="submit"
          className="px-5 py-2.5 bg-[var(--color-primary)] text-white text-sm font-medium rounded-xl hover:bg-[var(--color-primary-600)] transition-colors"
        >
          검색
        </button>
      </form>

      {/* 카테고리 그리드 */}
      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-3">
        {SYMPTOM_CATEGORIES.map((cat) => (
          <button
            key={cat.key}
            type="button"
            onClick={() => setExpandedCat(expandedCat === cat.key ? null : cat.key)}
            className={`flex flex-col items-center gap-2 p-4 rounded-xl border transition-all ${
              expandedCat === cat.key
                ? "border-[var(--color-primary)] bg-[var(--color-primary-50)] text-[var(--color-primary)]"
                : "border-gray-200 bg-white text-gray-600 hover:border-[var(--color-primary-100)] hover:shadow-sm"
            }`}
          >
            {CATEGORY_ICONS[cat.key]}
            <span className="text-sm font-medium">{cat.label}</span>
          </button>
        ))}
      </div>

      {/* 확장된 카테고리의 증상 칩 */}
      {expandedCat && (
        <div className="bg-gray-50 rounded-xl p-4">
          <p className="text-sm font-medium text-gray-600 mb-3">
            {SYMPTOM_CATEGORIES.find((c) => c.key === expandedCat)?.label} 관련 증상
          </p>
          <div className="flex flex-wrap gap-2">
            {SYMPTOM_CATEGORIES.find((c) => c.key === expandedCat)?.symptoms.map(
              (s) => (
                <button
                  key={s.value}
                  type="button"
                  onClick={() => handleSymptomClick(s.value)}
                  className={`px-3 py-1.5 rounded-full text-sm font-medium border transition-all ${
                    selectedSymptom === s.value
                      ? "border-[var(--color-primary)] bg-[var(--color-primary)] text-white"
                      : "border-gray-200 bg-white text-gray-600 hover:border-[var(--color-primary-100)] hover:text-[var(--color-primary)]"
                  }`}
                >
                  {s.label}
                </button>
              ),
            )}
          </div>
        </div>
      )}

      {/* 검색 결과 */}
      {loading && (
        <div className="text-center py-8 text-gray-400 text-sm">
          검색 중...
        </div>
      )}

      {!loading && searched && (
        <div>
          <h2 className="text-lg font-semibold text-gray-800 mb-3">
            &quot;{selectedSymptom}&quot; 관련 의약품
            <span className="text-sm font-normal text-gray-400 ml-2">
              {total.toLocaleString()}건
            </span>
          </h2>

          {results.length === 0 ? (
            <p className="text-center py-8 text-gray-400 text-sm">
              검색 결과가 없습니다.
            </p>
          ) : (
            <div className="space-y-2">
              {results.map((drug) => (
                <Link
                  key={drug.id}
                  href={`/drugs/${drug.slug}`}
                  className="block p-4 bg-white rounded-xl border border-gray-200 hover:border-[var(--color-primary-100)] hover:shadow-sm transition-all"
                >
                  <div className="flex items-start justify-between gap-3">
                    <div className="min-w-0">
                      <p className="font-medium text-gray-900 truncate">
                        {drug.item_name}
                      </p>
                      {drug.entp_name && (
                        <p className="text-sm text-gray-500">{drug.entp_name}</p>
                      )}
                    </div>
                    {drug.etc_otc_code && (
                      <span className="shrink-0 text-xs px-2 py-0.5 rounded-md bg-blue-50 text-blue-700">
                        {drug.etc_otc_code}
                      </span>
                    )}
                  </div>
                </Link>
              ))}
            </div>
          )}

          {/* 페이지네이션 */}
          {totalPages > 1 && (
            <div className="flex justify-center gap-1 pt-4">
              <button
                type="button"
                onClick={() => handlePageChange(page - 1)}
                disabled={page <= 1}
                className="px-3 py-1.5 text-sm border border-gray-200 rounded-lg disabled:opacity-30 hover:bg-gray-50"
              >
                이전
              </button>
              <span className="px-3 py-1.5 text-sm text-gray-500">
                {page} / {totalPages}
              </span>
              <button
                type="button"
                onClick={() => handlePageChange(page + 1)}
                disabled={page >= totalPages}
                className="px-3 py-1.5 text-sm border border-gray-200 rounded-lg disabled:opacity-30 hover:bg-gray-50"
              >
                다음
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
