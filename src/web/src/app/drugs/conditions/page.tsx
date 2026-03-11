"use client";

import { useState, useCallback, useEffect, Suspense } from "react";
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

/** 주의사항 텍스트에서 키워드들 중 가장 많이 포함된 구간을 잘라낸다. */
function extractSnippet(text: string, keywords: string[], radius = 50): string {
  if (keywords.length === 0) return text.slice(0, radius * 2);
  let bestIdx = -1;
  let bestCount = 0;
  for (const kw of keywords) {
    const idx = text.indexOf(kw);
    if (idx < 0) continue;
    const windowStart = Math.max(0, idx - radius);
    const windowEnd = Math.min(text.length, idx + kw.length + radius);
    const window = text.slice(windowStart, windowEnd);
    const count = keywords.filter((k) => window.includes(k)).length;
    if (count > bestCount) {
      bestCount = count;
      bestIdx = idx;
    }
  }
  if (bestIdx < 0) return text.slice(0, radius * 2);
  const start = Math.max(0, bestIdx - radius);
  const end = Math.min(text.length, bestIdx + radius * 2);
  const prefix = start > 0 ? "..." : "";
  const suffix = end < text.length ? "..." : "";
  return `${prefix}${text.slice(start, end)}${suffix}`;
}

/** 텍스트에서 여러 키워드를 하이라이트하여 ReactNode 배열로 반환한다. */
function highlightKeywords(text: string, keywords: string[]) {
  if (keywords.length === 0) return [text];
  const escaped = keywords.map((k) => k.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"));
  const regex = new RegExp(`(${escaped.join("|")})`, "g");
  const parts = text.split(regex);
  return parts.map((part, i) =>
    keywords.includes(part) ? (
      <mark key={i} className="bg-orange-100 text-orange-800 rounded px-0.5">
        {part}
      </mark>
    ) : (
      <span key={i}>{part}</span>
    ),
  );
}

function ConditionsContent() {
  const searchParams = useSearchParams();
  const [query, setQuery] = useState("");
  const [activeKeywords, setActiveKeywords] = useState<string[]>([]);
  const [showResults, setShowResults] = useState(false);
  const [state, setState] = useState<SearchState>(INITIAL_STATE);

  const doSearch = useCallback(async (keywords: string[], page = 1) => {
    const q = keywords.join(" ").trim();
    if (!q) return;
    setState((prev) => ({ ...prev, isLoading: true, error: null }));
    try {
      const res = await searchDrugsByCondition(q, page);
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
  const initialQuery = searchParams.get("q");
  useEffect(() => {
    if (initialQuery) {
      const keywords = initialQuery.trim().split(/\s+/).filter(Boolean);
      setQuery("");
      setActiveKeywords(keywords);
      doSearch(keywords);
    }
  }, [initialQuery, doSearch]);

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    const inputKeywords = query.trim().split(/\s+/).filter(Boolean);
    if (inputKeywords.length === 0) return;
    const merged = [...new Set([...activeKeywords, ...inputKeywords])];
    setActiveKeywords(merged);
    setQuery("");
    doSearch(merged);
  }

  function handleCardClick(keyword: string) {
    const newKeywords = activeKeywords.includes(keyword)
      ? activeKeywords.filter((k) => k !== keyword)
      : [...activeKeywords, keyword];
    setActiveKeywords(newKeywords);
    if (newKeywords.length > 0) {
      doSearch(newKeywords);
    } else {
      setShowResults(false);
      setState(INITIAL_STATE);
    }
  }

  function handleRemoveTag(keyword: string) {
    const newKeywords = activeKeywords.filter((k) => k !== keyword);
    setActiveKeywords(newKeywords);
    if (newKeywords.length > 0) {
      doSearch(newKeywords);
    } else {
      setShowResults(false);
      setState(INITIAL_STATE);
    }
  }

  function handlePageChange(newPage: number) {
    doSearch(activeKeywords, newPage);
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  function handleBackToCards() {
    setShowResults(false);
    setActiveKeywords([]);
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
        <p className="text-gray-500 dark:text-gray-400 mb-6">
          질환이나 상태를 선택하면 해당 조건에서 주의가 필요한 의약품을 확인할 수 있습니다.
        </p>

        {/* 검색 입력 */}
        <form onSubmit={handleSubmit} className="mb-4">
          <div className="flex gap-2">
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="키워드를 입력하세요 (여러 개는 공백으로 구분)"
              className="flex-1 px-4 py-2.5 border border-gray-300 dark:border-gray-600 rounded-xl focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)] focus:border-transparent text-sm"
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

        {/* 키워드 태그 */}
        {activeKeywords.length > 0 && (
          <div className="flex flex-wrap items-center gap-2 mb-4">
            <span className="text-xs text-gray-500 dark:text-gray-400">
              {activeKeywords.length}개 키워드로 검색 중
            </span>
            {activeKeywords.map((kw) => (
              <span
                key={kw}
                className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-medium bg-[var(--color-primary)] text-white"
              >
                {kw}
                <button
                  type="button"
                  onClick={() => handleRemoveTag(kw)}
                  className="ml-0.5 hover:bg-white/20 rounded-full p-0.5 transition-colors"
                  aria-label={`${kw} 제거`}
                >
                  <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </span>
            ))}
          </div>
        )}

        {/* 질환 카드 그리드 (검색 결과가 없을 때 표시) */}
        {!showResults && (
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
            {CONDITIONS.map((cond) => (
              <div
                key={cond.keyword}
                className="text-left p-4 border border-gray-200 dark:border-gray-700 rounded-xl hover:border-[var(--color-primary-100)] hover:bg-[var(--color-primary-50)]/30 dark:hover:bg-[var(--color-primary-900)]/30 transition-colors"
              >
                <button
                  onClick={() => handleCardClick(cond.keyword)}
                  className="w-full text-left"
                >
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-lg" role="img" aria-label={cond.label}>{cond.icon}</span>
                    <h3 className="text-sm font-semibold text-gray-900 dark:text-white">{cond.label}</h3>
                  </div>
                  <p className="text-xs text-gray-400 dark:text-gray-500 leading-snug">{cond.description}</p>
                </button>
                <Link
                  href={`/conditions/${cond.slug}`}
                  className="inline-block mt-2 text-xs text-[var(--color-primary)] hover:underline"
                >
                  상세 목록 보기 &rarr;
                </Link>
              </div>
            ))}
          </div>
        )}

        {/* 검색 결과 */}
        {showResults && (
          <>
            <div className="flex items-center justify-between mb-4">
              <p className="text-sm text-gray-500 dark:text-gray-400">
                <span className="font-semibold text-[var(--color-primary)]">{activeKeywords.join(" ")}</span>
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
              <div className="text-center py-12 text-gray-400 dark:text-gray-500">검색 중...</div>
            )}

            {/* 에러 */}
            {state.error && (
              <div className="text-center py-12 text-red-500">{state.error}</div>
            )}

            {!state.isLoading && !state.error && (
              <>
                {state.items.length === 0 ? (
                  <div className="text-center py-12 text-gray-400 dark:text-gray-500">
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
                            className="block p-4 border border-gray-200 dark:border-gray-700 rounded-xl hover:border-[var(--color-primary-100)] hover:bg-[var(--color-primary-50)]/30 transition-colors"
                          >
                            <div className="flex items-start gap-3">
                              {drug.item_image && (
                                <img
                                  src={drug.item_image}
                                  alt={drug.item_name}
                                  className="w-12 h-12 object-contain rounded-lg bg-gray-50 dark:bg-gray-800 shrink-0"
                                  onError={(e) => { e.currentTarget.style.display = "none"; }}
                                />
                              )}
                              <div className="min-w-0 flex-1">
                                <h3 className="text-sm font-semibold text-gray-900 dark:text-white truncate">
                                  {drug.item_name}
                                </h3>
                                {drug.entp_name && (
                                  <p className="text-xs text-gray-400 dark:text-gray-500 mt-0.5">{drug.entp_name}</p>
                                )}
                                {cautionText && (
                                  <p className="text-xs text-gray-500 dark:text-gray-400 mt-1 leading-relaxed">
                                    {highlightKeywords(extractSnippet(cautionText, activeKeywords), activeKeywords)}
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
                      aria-label="이전 페이지"
                      className="px-3 py-1.5 text-sm rounded-lg border border-gray-200 dark:border-gray-700 disabled:opacity-30 hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
                    >
                      이전
                    </button>
                    <span className="text-sm text-gray-500 dark:text-gray-400">
                      {state.page} / {state.totalPages}
                    </span>
                    <button
                      onClick={() => handlePageChange(state.page + 1)}
                      disabled={state.page >= state.totalPages}
                      aria-label="다음 페이지"
                      className="px-3 py-1.5 text-sm rounded-lg border border-gray-200 dark:border-gray-700 disabled:opacity-30 hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
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

export default function ConditionsPage() {
  return (
    <Suspense>
      <ConditionsContent />
    </Suspense>
  );
}
