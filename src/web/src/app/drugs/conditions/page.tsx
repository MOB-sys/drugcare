"use client";

import { useState, useCallback, useEffect } from "react";
import { useSearchParams } from "next/navigation";
import Link from "next/link";
import { searchDrugsByCondition } from "@/lib/api/drugs";
import { CONDITIONS } from "@/lib/data/conditions";
import { Breadcrumbs } from "@/components/common/Breadcrumbs";
import type { DrugConditionItem } from "@/types/drug";

interface SearchState {
  items: DrugConditionItem[];
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

/** 주의사항 텍스트에서 키워드 주변을 잘라낸다. */
function extractSnippet(text: string, keyword: string, radius = 50): string {
  const idx = text.indexOf(keyword);
  if (idx < 0) return text.slice(0, radius * 2);
  const start = Math.max(0, idx - radius);
  const end = Math.min(text.length, idx + keyword.length + radius);
  const prefix = start > 0 ? "..." : "";
  const suffix = end < text.length ? "..." : "";
  return `${prefix}${text.slice(start, end)}${suffix}`;
}

export default function ConditionsPage() {
  const searchParams = useSearchParams();
  const [query, setQuery] = useState("");
  const [activeKeyword, setActiveKeyword] = useState("");
  const [showResults, setShowResults] = useState(false);
  const [state, setState] = useState<SearchState>(INITIAL_STATE);

  const doSearch = useCallback(async (q: string, page = 1) => {
    if (!q.trim()) return;
    setState((prev) => ({ ...prev, isLoading: true, error: null }));
    try {
      const res = await searchDrugsByCondition(q.trim(), page);
      setState({
        items: res.items,
        total: res.total,
        page: res.page,
        totalPages: Math.ceil(res.total / 20),
        isLoading: false,
        error: null,
        searched: true,
      });
      setShowResults(true);
    } catch {
      setState((prev) => ({
        ...prev,
        isLoading: false,
        error: "검색 중 오류가 발생했습니다. 다시 시도해주세요.",
        searched: true,
      }));
      setShowResults(true);
    }
  }, []);

  /* URL 파라미터로 자동 검색 */
  useEffect(() => {
    const q = searchParams.get("q");
    if (q) {
      setQuery(q);
      setActiveKeyword(q);
      doSearch(q);
    }
  }, [searchParams, doSearch]);

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setActiveKeyword(query.trim());
    doSearch(query);
  }

  function handleCardClick(keyword: string) {
    setQuery(keyword);
    setActiveKeyword(keyword);
    doSearch(keyword);
  }

  function handlePageChange(newPage: number) {
    doSearch(activeKeyword, newPage);
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  function handleBackToCards() {
    setShowResults(false);
    setActiveKeyword("");
    setQuery("");
    setState(INITIAL_STATE);
  }

  return (
    <>
      <Breadcrumbs
        items={[
          { label: "홈", href: "/" },
          { label: "의약품", href: "/drugs" },
          { label: "질환별 주의사항" },
        ]}
      />

      <section className="max-w-2xl mx-auto px-4 py-6">
        <h1 className="text-2xl font-bold text-[var(--color-primary)] mb-2">
          질환별 약물 주의사항
        </h1>
        <p className="text-gray-500 mb-6">
          질환이나 상태를 선택하면 해당 조건에서 주의가 필요한 의약품을 확인할 수 있습니다.
        </p>

        {/* 검색 입력 */}
        <form onSubmit={handleSubmit} className="mb-6">
          <div className="flex gap-2">
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="질환 키워드 (예: 당뇨, 고혈압, 임산부)"
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

        {/* 질환 카드 그리드 (검색 결과가 없을 때 표시) */}
        {!showResults && (
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
            {CONDITIONS.map((cond) => (
              <button
                key={cond.keyword}
                onClick={() => handleCardClick(cond.keyword)}
                className="text-left p-4 border border-gray-200 rounded-xl hover:border-[var(--color-primary-100)] hover:bg-[var(--color-primary-50)]/30 transition-colors"
              >
                <h3 className="text-sm font-semibold text-gray-900 mb-1">{cond.label}</h3>
                <p className="text-[11px] text-gray-400 leading-snug">{cond.description}</p>
              </button>
            ))}
          </div>
        )}

        {/* 검색 결과 */}
        {showResults && (
          <>
            <div className="flex items-center justify-between mb-4">
              <p className="text-sm text-gray-500">
                <span className="font-semibold text-[var(--color-primary)]">{activeKeyword}</span>
                {" "}관련 주의 의약품 {state.total.toLocaleString()}건
              </p>
              <button
                onClick={handleBackToCards}
                className="text-xs text-[var(--color-primary)] hover:underline"
              >
                질환 목록으로
              </button>
            </div>

            {/* 로딩 */}
            {state.isLoading && (
              <div className="text-center py-12 text-gray-400">검색 중...</div>
            )}

            {/* 에러 */}
            {state.error && (
              <div className="text-center py-12 text-red-500">{state.error}</div>
            )}

            {!state.isLoading && !state.error && (
              <>
                {state.items.length === 0 ? (
                  <div className="text-center py-12 text-gray-400">
                    검색 결과가 없습니다. 다른 키워드로 검색해보세요.
                  </div>
                ) : (
                  <ul className="space-y-3">
                    {state.items.map((drug) => {
                      const cautionText = drug.atpn_warn_qesitm || drug.atpn_qesitm || "";
                      return (
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
                                {cautionText && (
                                  <p className="text-xs text-gray-500 mt-1 leading-relaxed">
                                    {extractSnippet(cautionText, activeKeyword).split(activeKeyword).map((part, i, arr) =>
                                      i < arr.length - 1 ? (
                                        <span key={i}>
                                          {part}
                                          <mark className="bg-orange-100 text-orange-800 rounded px-0.5">
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
                      );
                    })}
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
          </>
        )}

        {/* 면책조항 */}
        <div className="mt-8 p-4 bg-amber-50 border border-amber-200 rounded-xl">
          <p className="text-xs text-amber-700 leading-relaxed">
            질환별 주의사항은 참고용이며, 복용 전 반드시 의사/약사와 상담하세요.
            이 서비스는 의사/약사의 전문적 판단을 대체하지 않습니다.
          </p>
        </div>
      </section>
    </>
  );
}
