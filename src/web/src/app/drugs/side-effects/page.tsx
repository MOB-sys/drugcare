"use client";

import { useState, useCallback } from "react";
import Link from "next/link";
import { searchDrugsBySideEffect } from "@/lib/api/drugs";
import { COMMON_SIDE_EFFECTS } from "@/lib/data/commonSideEffects";
import { Breadcrumbs } from "@/components/common/Breadcrumbs";
import type { DrugSideEffectItem } from "@/types/drug";

interface SearchState {
  items: DrugSideEffectItem[];
  total: number;
  page: number;
  totalPages: number;
  isLoading: boolean;
  error: string | null;
  searched: boolean;
}

const INITIAL_STATE: SearchState = {
  items: [],
  total: 0,
  page: 1,
  totalPages: 0,
  isLoading: false,
  error: null,
  searched: false,
};

/** 텍스트에서 키워드 주변을 잘라내어 반환한다. */
function extractSnippet(text: string, keyword: string, radius = 40): string {
  const idx = text.indexOf(keyword);
  if (idx < 0) return text.slice(0, radius * 2);
  const start = Math.max(0, idx - radius);
  const end = Math.min(text.length, idx + keyword.length + radius);
  const prefix = start > 0 ? "..." : "";
  const suffix = end < text.length ? "..." : "";
  return `${prefix}${text.slice(start, end)}${suffix}`;
}

export default function SideEffectsPage() {
  const [query, setQuery] = useState("");
  const [activeKeyword, setActiveKeyword] = useState("");
  const [state, setState] = useState<SearchState>(INITIAL_STATE);

  const doSearch = useCallback(async (q: string, page = 1) => {
    if (!q.trim()) return;
    setState((prev) => ({ ...prev, isLoading: true, error: null }));
    try {
      const res = await searchDrugsBySideEffect(q.trim(), page);
      setState({
        items: res.items,
        total: res.total,
        page: res.page,
        totalPages: Math.ceil(res.total / 20),
        isLoading: false,
        error: null,
        searched: true,
      });
    } catch {
      setState((prev) => ({
        ...prev,
        isLoading: false,
        error: "검색 중 오류가 발생했습니다. 다시 시도해주세요.",
        searched: true,
      }));
    }
  }, []);

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setActiveKeyword(query.trim());
    doSearch(query);
  }

  function handleChipClick(keyword: string) {
    setQuery(keyword);
    setActiveKeyword(keyword);
    doSearch(keyword);
  }

  function handlePageChange(newPage: number) {
    doSearch(activeKeyword, newPage);
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  return (
    <>
      <Breadcrumbs
        items={[
          { label: "홈", href: "/" },
          { label: "의약품", href: "/drugs" },
          { label: "부작용 역검색" },
        ]}
      />

      <section className="max-w-2xl mx-auto px-4 py-6">
        <h1 className="text-2xl font-bold text-[var(--color-primary)] mb-2">
          부작용 역검색
        </h1>
        <p className="text-gray-500 mb-6">
          부작용 키워드를 입력하면 해당 부작용이 보고된 의약품을 찾아볼 수 있습니다.
        </p>

        {/* 검색 입력 */}
        <form onSubmit={handleSubmit} className="mb-4">
          <div className="flex gap-2">
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="부작용 키워드 (예: 두통, 어지러움)"
              className="flex-1 px-4 py-2.5 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)] focus:border-transparent text-sm"
            />
            <button
              type="submit"
              disabled={!query.trim() || state.isLoading}
              className="px-5 py-2.5 bg-[var(--color-primary)] text-white rounded-xl text-sm font-medium hover:bg-[var(--color-primary-dark)] disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              검색
            </button>
          </div>
        </form>

        {/* 빠른 필터 칩 */}
        <div className="flex flex-wrap gap-2 mb-6">
          {COMMON_SIDE_EFFECTS.map((se) => (
            <button
              key={se.keyword}
              onClick={() => handleChipClick(se.keyword)}
              className={`px-3 py-1.5 rounded-full text-xs font-medium transition-colors ${
                activeKeyword === se.keyword
                  ? "bg-[var(--color-primary)] text-white"
                  : "bg-gray-100 text-gray-600 hover:bg-gray-200"
              }`}
            >
              {se.label}
            </button>
          ))}
        </div>

        {/* 로딩 */}
        {state.isLoading && (
          <div className="text-center py-12 text-gray-400">검색 중...</div>
        )}

        {/* 에러 */}
        {state.error && (
          <div className="text-center py-12 text-red-500">{state.error}</div>
        )}

        {/* 결과 */}
        {!state.isLoading && !state.error && state.searched && (
          <>
            <p className="text-sm text-gray-500 mb-4">
              <span className="font-semibold text-[var(--color-primary)]">{activeKeyword}</span>
              {" "}관련 의약품 {state.total.toLocaleString()}건
            </p>

            {state.items.length === 0 ? (
              <div className="text-center py-12 text-gray-400">
                검색 결과가 없습니다. 다른 키워드로 검색해보세요.
              </div>
            ) : (
              <ul className="space-y-3">
                {state.items.map((drug) => (
                  <li key={drug.id}>
                    <Link
                      href={`/drugs/${drug.slug}`}
                      className="block p-4 border border-gray-200 rounded-xl hover:border-[var(--color-primary-100)] hover:bg-[var(--color-primary-50)]/30 transition-colors"
                    >
                      <div className="flex items-start gap-3">
                        {drug.item_image && (
                          <img
                            src={drug.item_image}
                            alt={drug.item_name}
                            className="w-12 h-12 object-contain rounded-lg bg-gray-50 shrink-0"
                          />
                        )}
                        <div className="min-w-0 flex-1">
                          <h3 className="text-sm font-semibold text-gray-900 truncate">
                            {drug.item_name}
                          </h3>
                          {drug.entp_name && (
                            <p className="text-xs text-gray-400 mt-0.5">{drug.entp_name}</p>
                          )}
                          {drug.se_qesitm && (
                            <p className="text-xs text-gray-500 mt-1 leading-relaxed">
                              {extractSnippet(drug.se_qesitm, activeKeyword).split(activeKeyword).map((part, i, arr) =>
                                i < arr.length - 1 ? (
                                  <span key={i}>
                                    {part}
                                    <mark className="bg-yellow-200 text-gray-900 rounded px-0.5">
                                      {activeKeyword}
                                    </mark>
                                  </span>
                                ) : (
                                  <span key={i}>{part}</span>
                                ),
                              )}
                            </p>
                          )}
                        </div>
                      </div>
                    </Link>
                  </li>
                ))}
              </ul>
            )}

            {/* 페이지네이션 */}
            {state.totalPages > 1 && (
              <nav className="flex justify-center items-center gap-2 mt-8">
                <button
                  onClick={() => handlePageChange(state.page - 1)}
                  disabled={state.page <= 1}
                  className="px-3 py-1.5 text-sm rounded-lg border border-gray-200 disabled:opacity-30 hover:bg-gray-50 transition-colors"
                >
                  이전
                </button>
                <span className="text-sm text-gray-500">
                  {state.page} / {state.totalPages}
                </span>
                <button
                  onClick={() => handlePageChange(state.page + 1)}
                  disabled={state.page >= state.totalPages}
                  className="px-3 py-1.5 text-sm rounded-lg border border-gray-200 disabled:opacity-30 hover:bg-gray-50 transition-colors"
                >
                  다음
                </button>
              </nav>
            )}
          </>
        )}

        {/* 면책조항 */}
        <div className="mt-8 p-4 bg-amber-50 border border-amber-200 rounded-xl">
          <p className="text-xs text-amber-700 leading-relaxed">
            부작용 정보는 참고용이며, 증상이 있으면 의사/약사와 상담하세요.
            이 서비스는 의사/약사의 전문적 판단을 대체하지 않습니다.
          </p>
        </div>
      </section>
    </>
  );
}
