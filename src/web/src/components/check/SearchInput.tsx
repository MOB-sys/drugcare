"use client";

import { useState, useRef, useEffect } from "react";

const POPULAR_SEARCHES = [
  "비타민D", "오메가3", "타이레놀", "마그네슘", "유산균",
  "아스피린", "철분", "비타민C", "혈압약", "종합비타민",
];

interface SearchInputProps {
  value: string;
  onChange: (value: string) => void;
  recentSearches?: string[];
  onSearchSelect?: (query: string) => void;
  onRemoveRecent?: (query: string) => void;
  onClearRecent?: () => void;
}

export function SearchInput({
  value,
  onChange,
  recentSearches = [],
  onSearchSelect,
  onRemoveRecent,
  onClearRecent,
}: SearchInputProps) {
  const [showDropdown, setShowDropdown] = useState(false);
  const wrapperRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function handleClickOutside(e: MouseEvent) {
      if (wrapperRef.current && !wrapperRef.current.contains(e.target as Node)) {
        setShowDropdown(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  function handleSelect(query: string) {
    onChange(query);
    onSearchSelect?.(query);
    setShowDropdown(false);
  }

  const shouldShowDropdown = showDropdown && !value.trim() && (recentSearches.length > 0 || POPULAR_SEARCHES.length > 0);

  return (
    <div ref={wrapperRef} className="relative">
      <svg
        className="absolute left-3.5 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
        />
      </svg>
      <label htmlFor="search-input" className="sr-only">약물 또는 영양제 검색</label>
      <input
        id="search-input"
        type="text"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        onFocus={() => setShowDropdown(true)}
        placeholder="약물 또는 영양제를 검색하세요"
        aria-label="약물 또는 영양제 검색"
        role="combobox"
        aria-expanded={shouldShowDropdown}
        autoComplete="off"
        className="w-full pl-11 pr-10 py-3 border border-gray-200 dark:border-gray-700 rounded-xl shadow-sm focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)] focus:border-transparent text-base bg-white dark:bg-gray-800 dark:text-gray-100"
      />
      {value && (
        <button
          onClick={() => onChange("")}
          className="absolute right-2.5 top-1/2 -translate-y-1/2 p-1 w-7 h-7 text-gray-400 hover:text-gray-600"
          aria-label="검색어 지우기"
        >
          <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M6 18L18 6M6 6l12 12"
            />
          </svg>
        </button>
      )}

      {/* 드롭다운: 최근 검색 + 인기 검색어 */}
      {shouldShowDropdown && (
        <div className="absolute top-full left-0 right-0 mt-1 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl shadow-lg z-20 overflow-hidden">
          {/* 최근 검색 */}
          {recentSearches.length > 0 && (
            <div className="p-3 border-b border-gray-100 dark:border-gray-700">
              <div className="flex items-center justify-between mb-2">
                <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider">최근 검색</p>
                {onClearRecent && (
                  <button
                    onClick={onClearRecent}
                    className="text-xs text-gray-400 hover:text-gray-600 transition-colors"
                  >
                    전체 삭제
                  </button>
                )}
              </div>
              <div className="flex flex-wrap gap-1.5">
                {recentSearches.map((q) => (
                  <div key={q} className="inline-flex items-center gap-1 rounded-lg bg-gray-50 dark:bg-gray-700 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors group">
                    <button
                      onClick={() => handleSelect(q)}
                      className="pl-2.5 py-1 hover:text-[var(--color-primary)]"
                    >
                      {q}
                    </button>
                    {onRemoveRecent && (
                      <button
                        onClick={() => onRemoveRecent(q)}
                        className="pr-2 py-1 text-gray-300 hover:text-gray-500 opacity-0 group-hover:opacity-100 transition-opacity"
                        aria-label={`${q} 삭제`}
                      >
                        <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                        </svg>
                      </button>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* 인기 검색어 */}
          <div className="p-3">
            <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">인기 검색어</p>
            <div className="flex flex-wrap gap-1.5">
              {POPULAR_SEARCHES.map((q) => (
                <button
                  key={q}
                  onClick={() => handleSelect(q)}
                  className="px-2.5 py-1 rounded-lg bg-[var(--color-primary-50)] text-sm text-[var(--color-primary)] hover:bg-[var(--color-primary-100)] transition-colors"
                >
                  {q}
                </button>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
