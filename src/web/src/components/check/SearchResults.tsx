"use client";

import { SearchResultItem } from "./SearchResultItem";
import type { SearchResultItem as SearchResultItemType } from "@/lib/hooks/useSearch";

interface SearchResultsProps {
  results: SearchResultItemType[];
  isLoading: boolean;
  query: string;
  searchError?: string | null;
  isSelected: (id: number, type: string) => boolean;
  canAddMore: boolean;
  onToggle: (item: { item_type: "drug" | "supplement"; item_id: number; name: string }) => void;
}

export function SearchResults({
  results,
  isLoading,
  query,
  searchError,
  isSelected,
  canAddMore,
  onToggle,
}: SearchResultsProps) {
  if (isLoading) {
    return (
      <div className="py-12 text-center text-gray-400">
        <div className="inline-block w-6 h-6 border-2 border-[var(--color-primary-100)] border-t-[var(--color-primary)] rounded-full animate-spin" />
        <p className="mt-2 text-sm">검색 중...</p>
      </div>
    );
  }

  if (!query.trim()) {
    return (
      <div className="py-12 text-center text-gray-400">
        <p className="text-sm">약물이나 영양제 이름을 검색해보세요</p>
      </div>
    );
  }

  if (searchError) {
    return (
      <div className="py-12 text-center">
        <div className="w-10 h-10 mx-auto mb-3 rounded-full bg-red-50 flex items-center justify-center">
          <svg className="w-5 h-5 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01" />
          </svg>
        </div>
        <p className="text-sm text-red-600 font-medium">{searchError}</p>
      </div>
    );
  }

  if (results.length === 0) {
    return (
      <div className="py-12 text-center text-gray-400">
        <p className="text-sm">&quot;{query}&quot;에 대한 검색 결과가 없습니다</p>
      </div>
    );
  }

  return (
    <div className="divide-y divide-gray-100 max-h-80 overflow-y-auto scrollbar-thin">
      {results.map((r) => (
        <SearchResultItem
          key={`${r.item_type}-${r.item_id}`}
          name={r.name}
          sub={r.sub}
          itemType={r.item_type}
          itemId={r.item_id}
          selected={isSelected(r.item_id, r.item_type)}
          disabled={!canAddMore}
          onToggle={() => onToggle({ item_type: r.item_type, item_id: r.item_id, name: r.name })}
          showCabinetAdd
        />
      ))}
    </div>
  );
}
