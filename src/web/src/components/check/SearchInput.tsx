"use client";

import { useState, useRef, useEffect, useCallback } from "react";
import { SearchIcon, CloseIcon } from "@/components/icons";
import { fetchSearchSuggestions, type SearchSuggestion } from "@/lib/api/search";

const POPULAR_SEARCHES = [
  "비타민D", "오메가3", "타이레놀", "마그네슘", "유산균",
  "아스피린", "철분", "비타민C", "혈압약", "종합비타민",
];

const TYPE_LABELS: Record<string, string> = {
  drug: "약물",
  supplement: "영양제",
  food: "식품",
  herbal: "한약재",
};

const TYPE_COLORS: Record<string, string> = {
  drug: "bg-blue-50 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300",
  supplement: "bg-emerald-50 dark:bg-emerald-900/30 text-emerald-700 dark:text-emerald-300",
  food: "bg-orange-50 dark:bg-orange-900/30 text-orange-700 dark:text-orange-300",
  herbal: "bg-purple-50 dark:bg-purple-900/30 text-purple-700 dark:text-purple-300",
};

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
  const [suggestions, setSuggestions] = useState<SearchSuggestion[]>([]);
  const [loadingSuggestions, setLoadingSuggestions] = useState(false);
  const wrapperRef = useRef<HTMLDivElement>(null);
  const debounceRef = useRef<ReturnType<typeof setTimeout>>(undefined);

  useEffect(() => {
    function handleClickOutside(e: MouseEvent) {
      if (wrapperRef.current && !wrapperRef.current.contains(e.target as Node)) {
        setShowDropdown(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  // 자동완성 제안 fetching (디바운스 300ms)
  const fetchSuggestions = useCallback((query: string) => {
    if (debounceRef.current) clearTimeout(debounceRef.current);

    if (query.trim().length < 2) {
      setSuggestions([]);
      return;
    }

    setLoadingSuggestions(true);
    debounceRef.current = setTimeout(async () => {
      try {
        const results = await fetchSearchSuggestions(query.trim(), 8);
        setSuggestions(results);
      } catch {
        setSuggestions([]);
      } finally {
        setLoadingSuggestions(false);
      }
    }, 300);
  }, []);

  function handleChange(newValue: string) {
    onChange(newValue);
    fetchSuggestions(newValue);
  }

  function handleSelect(query: string) {
    onChange(query);
    onSearchSelect?.(query);
    setShowDropdown(false);
    setSuggestions([]);
  }

  const hasSuggestions = value.trim().length >= 2 && suggestions.length > 0;
  const showEmptyState = showDropdown && !value.trim() && (recentSearches.length > 0 || POPULAR_SEARCHES.length > 0);
  const showSuggestionList = showDropdown && hasSuggestions;

  return (
    <div ref={wrapperRef} className="relative">
      <SearchIcon className="absolute left-3.5 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400 dark:text-gray-500" />
      <label htmlFor="search-input" className="sr-only">약물 또는 영양제 검색</label>
      <input
        id="search-input"
        type="text"
        value={value}
        onChange={(e) => handleChange(e.target.value)}
        onFocus={() => setShowDropdown(true)}
        placeholder="약물 또는 영양제를 검색하세요"
        aria-label="약물 또는 영양제 검색"
        role="combobox"
        aria-expanded={showEmptyState || showSuggestionList}
        aria-controls={showEmptyState || showSuggestionList ? "search-dropdown" : undefined}
        autoComplete="off"
        maxLength={200}
        className="w-full pl-11 pr-10 py-3 border border-gray-200 dark:border-gray-700 rounded-xl shadow-sm focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)] focus:border-transparent text-base bg-white dark:bg-gray-800 dark:text-gray-100"
      />
      {value && (
        <button
          onClick={() => { onChange(""); setSuggestions([]); }}
          className="absolute right-2.5 top-1/2 -translate-y-1/2 p-1.5 w-8 h-8 text-gray-400 dark:text-gray-500 hover:text-gray-600 dark:hover:text-gray-300"
          aria-label="검색어 지우기"
        >
          <CloseIcon className="w-full h-full" />
        </button>
      )}

      {/* 자동완성 제안 드롭다운 */}
      {showSuggestionList && (
        <div id="search-dropdown" role="listbox" className="absolute top-full left-0 right-0 mt-1 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl shadow-lg z-20 overflow-hidden">
          <div className="p-2">
            {suggestions.map((s, i) => (
              <button
                key={`${s.type}-${s.slug}-${i}`}
                onClick={() => handleSelect(s.name)}
                role="option"
                className="w-full flex items-center gap-2 px-3 py-2 text-left rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
              >
                <span className="text-sm text-gray-900 dark:text-gray-100 flex-1 truncate">{s.name}</span>
                <span className={`px-1.5 py-0.5 rounded text-[10px] font-medium shrink-0 ${TYPE_COLORS[s.type] || ""}`}>
                  {TYPE_LABELS[s.type] || s.type}
                </span>
              </button>
            ))}
          </div>
          {loadingSuggestions && (
            <div className="px-3 py-2 text-xs text-gray-400 dark:text-gray-500 text-center">검색 중...</div>
          )}
        </div>
      )}

      {/* 드롭다운: 최근 검색 + 인기 검색어 (빈 입력 시) */}
      {showEmptyState && !showSuggestionList && (
        <div id="search-dropdown" role="listbox" className="absolute top-full left-0 right-0 mt-1 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl shadow-lg z-20 overflow-hidden">
          {/* 최근 검색 */}
          {recentSearches.length > 0 && (
            <div className="p-3 border-b border-gray-100 dark:border-gray-700">
              <div className="flex items-center justify-between mb-2">
                <p className="text-xs font-semibold text-gray-400 dark:text-gray-500 uppercase tracking-wider">최근 검색</p>
                {onClearRecent && (
                  <button
                    onClick={onClearRecent}
                    className="text-xs text-gray-400 dark:text-gray-500 hover:text-gray-600 dark:hover:text-gray-300 transition-colors"
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
                        className="pr-2 py-1 text-gray-300 dark:text-gray-600 hover:text-gray-500 dark:hover:text-gray-400 opacity-0 group-hover:opacity-100 transition-opacity"
                        aria-label={`${q} 삭제`}
                      >
                        <CloseIcon className="w-3 h-3" />
                      </button>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* 인기 검색어 */}
          <div className="p-3">
            <p className="text-xs font-semibold text-gray-400 dark:text-gray-500 uppercase tracking-wider mb-2">인기 검색어</p>
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
