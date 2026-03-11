"use client";

import { useState, useCallback } from "react";
import Link from "next/link";
import { identifyDrug } from "@/lib/api/drugs";
import { PILL_COLORS, PILL_SHAPES } from "@/lib/data/pillCharacteristics";
import { Breadcrumbs } from "@/components/common/Breadcrumbs";
import type { DrugIdentifyItem } from "@/types/drug";

interface SearchState {
  items: DrugIdentifyItem[];
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

export default function IdentifyPage() {
  const [selectedColor, setSelectedColor] = useState<string | null>(null);
  const [selectedShape, setSelectedShape] = useState<string | null>(null);
  const [imprint, setImprint] = useState("");
  const [state, setState] = useState<SearchState>(INITIAL_STATE);
  const [failedImages, setFailedImages] = useState<Set<number>>(new Set());

  const doSearch = useCallback(
    async (color: string | null, shape: string | null, imp: string, page = 1) => {
      if (!color && !shape && !imp.trim()) return;
      setState((prev) => ({ ...prev, isLoading: true, error: null }));
      try {
        const res = await identifyDrug(color, shape, imp.trim() || null, page);
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
    },
    [],
  );

  function handleSearch() {
    doSearch(selectedColor, selectedShape, imprint);
  }

  function handlePageChange(newPage: number) {
    doSearch(selectedColor, selectedShape, imprint, newPage);
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  function handleReset() {
    setSelectedColor(null);
    setSelectedShape(null);
    setImprint("");
    setState(INITIAL_STATE);
  }

  const hasFilter = !!selectedColor || !!selectedShape || !!imprint.trim();

  return (
    <>
      <Breadcrumbs
        items={[
          { label: "홈", href: "/" },
          { label: "의약품", href: "/drugs" },
          { label: "약 식별" },
        ]}
      />

      <section className="max-w-2xl mx-auto px-4 py-6">
        <h1 className="text-2xl font-bold text-[var(--color-primary)] mb-2">
          약 식별
        </h1>
        <p className="text-gray-500 dark:text-gray-400 mb-6">
          약의 색상, 모양, 각인을 선택하면 해당하는 의약품을 찾아드립니다.
        </p>

        {/* 색상 선택 */}
        <div className="mb-5">
          <h2 className="text-sm font-semibold text-gray-700 dark:text-gray-200 mb-2">색상</h2>
          <div className="flex flex-wrap gap-2">
            {PILL_COLORS.map((color) => (
              <button
                key={color.value}
                onClick={() =>
                  setSelectedColor(selectedColor === color.value ? null : color.value)
                }
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium transition-all ${
                  selectedColor === color.value
                    ? "ring-2 ring-[var(--color-primary)] bg-[var(--color-primary-50)]"
                    : "bg-gray-50 dark:bg-gray-800 hover:bg-gray-100 dark:hover:bg-gray-700"
                }`}
                title={color.label}
              >
                <span
                  className="w-4 h-4 rounded-full border border-gray-300 dark:border-gray-600 shrink-0"
                  style={{ backgroundColor: color.hex }}
                />
                <span className="text-gray-700 dark:text-gray-200">{color.label}</span>
              </button>
            ))}
          </div>
        </div>

        {/* 모양 선택 */}
        <div className="mb-5">
          <h2 className="text-sm font-semibold text-gray-700 dark:text-gray-200 mb-2">모양</h2>
          <div className="flex flex-wrap gap-2">
            {PILL_SHAPES.map((shape) => (
              <button
                key={shape.value}
                onClick={() =>
                  setSelectedShape(selectedShape === shape.value ? null : shape.value)
                }
                className={`px-3 py-1.5 rounded-full text-xs font-medium transition-all ${
                  selectedShape === shape.value
                    ? "bg-[var(--color-primary)] text-white"
                    : "bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700"
                }`}
              >
                {shape.label}
              </button>
            ))}
          </div>
        </div>

        {/* 각인 입력 */}
        <div className="mb-5">
          <h2 className="text-sm font-semibold text-gray-700 dark:text-gray-200 mb-2">각인 문자</h2>
          <input
            type="text"
            value={imprint}
            onChange={(e) => setImprint(e.target.value)}
            placeholder="약에 새겨진 문자를 입력하세요"
            className="w-full px-4 py-2.5 border border-gray-300 dark:border-gray-600 rounded-xl focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)] focus:border-transparent text-sm"
          />
        </div>

        {/* 검색/초기화 버튼 */}
        <div className="flex gap-2 mb-6">
          <button
            onClick={handleSearch}
            disabled={!hasFilter || state.isLoading}
            className="flex-1 px-5 py-2.5 bg-[var(--color-primary)] text-white rounded-xl text-sm font-medium hover:bg-[var(--color-primary-dark)] disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            검색
          </button>
          <button
            onClick={handleReset}
            className="px-5 py-2.5 border border-gray-300 dark:border-gray-600 text-gray-600 dark:text-gray-300 rounded-xl text-sm font-medium hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
          >
            초기화
          </button>
        </div>

        {/* 현재 필터 표시 */}
        {hasFilter && (
          <div className="flex flex-wrap gap-1.5 mb-4">
            {selectedColor && (
              <span className="inline-flex items-center gap-1 px-2.5 py-1 bg-[var(--color-primary-50)] text-[var(--color-primary)] rounded-full text-xs">
                색상: {selectedColor}
              </span>
            )}
            {selectedShape && (
              <span className="inline-flex items-center gap-1 px-2.5 py-1 bg-[var(--color-primary-50)] text-[var(--color-primary)] rounded-full text-xs">
                모양: {selectedShape}
              </span>
            )}
            {imprint.trim() && (
              <span className="inline-flex items-center gap-1 px-2.5 py-1 bg-[var(--color-primary-50)] text-[var(--color-primary)] rounded-full text-xs">
                각인: {imprint.trim()}
              </span>
            )}
          </div>
        )}

        {/* 로딩 */}
        {state.isLoading && (
          <div className="text-center py-12 text-gray-400 dark:text-gray-500">검색 중...</div>
        )}

        {/* 에러 */}
        {state.error && (
          <div className="text-center py-12 text-red-500">{state.error}</div>
        )}

        {/* 결과 */}
        {!state.isLoading && !state.error && state.searched && (
          <>
            <p className="text-sm text-gray-500 dark:text-gray-400 mb-4">
              검색 결과 {state.total.toLocaleString()}건
            </p>

            {state.items.length === 0 ? (
              <div className="text-center py-12 text-gray-400 dark:text-gray-500">
                일치하는 의약품이 없습니다. 조건을 변경해보세요.
              </div>
            ) : (
              <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
                {state.items.map((drug) => (
                  <Link
                    key={drug.id}
                    href={`/drugs/${drug.slug}`}
                    className="block p-3 border border-gray-200 dark:border-gray-700 rounded-xl hover:border-[var(--color-primary-100)] hover:bg-[var(--color-primary-50)]/30 transition-colors"
                  >
                    {drug.item_image && !failedImages.has(drug.id) ? (
                      <img
                        src={drug.item_image}
                        alt={drug.item_name}
                        className="w-full h-24 object-contain rounded-lg bg-gray-50 dark:bg-gray-800 mb-2"
                        onError={() => {
                          setFailedImages((prev) => new Set(prev).add(drug.id));
                        }}
                      />
                    ) : (
                      <div className="w-full h-24 bg-gray-100 dark:bg-gray-800 rounded-lg mb-2 flex items-center justify-center">
                        <span className="text-gray-300 dark:text-gray-600 text-xs">이미지 없음</span>
                      </div>
                    )}
                    <h3 className="text-xs font-semibold text-gray-900 dark:text-white truncate">
                      {drug.item_name}
                    </h3>
                    {drug.chart && (
                      <p className="text-xs text-gray-400 dark:text-gray-500 mt-0.5 truncate">
                        {drug.chart}
                      </p>
                    )}
                  </Link>
                ))}
              </div>
            )}

            {/* 페이지네이션 */}
            {state.totalPages > 1 && (
              <nav className="flex justify-center items-center gap-2 mt-8">
                <button
                  onClick={() => handlePageChange(state.page - 1)}
                  disabled={state.page <= 1}
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
                  className="px-3 py-1.5 text-sm rounded-lg border border-gray-200 dark:border-gray-700 disabled:opacity-30 hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
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
            약 식별 결과는 참고용이며 정확한 확인은 약사에게 문의하세요.
            이 서비스는 의사/약사의 전문적 판단을 대체하지 않습니다.
          </p>
        </div>
      </section>
    </>
  );
}
