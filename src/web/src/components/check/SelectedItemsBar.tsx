"use client";

import type { SelectedItem } from "@/types/search";

interface SelectedItemsBarProps {
  items: SelectedItem[];
  onRemove: (id: number, type: string) => void;
  onClearAll: () => void;
}

export function SelectedItemsBar({ items, onRemove, onClearAll }: SelectedItemsBarProps) {
  if (items.length === 0) return null;

  return (
    <div className="bg-[var(--color-primary-50)] rounded-xl p-3">
      <div className="flex items-center justify-between mb-2">
        <span className="text-sm font-medium text-[var(--color-primary)]">
          선택된 항목 ({items.length}개)
        </span>
        <button
          onClick={onClearAll}
          className="text-xs text-gray-400 hover:text-gray-600"
        >
          전체 해제
        </button>
      </div>
      <div className="flex flex-wrap gap-2">
        {items.map((item) => (
          <span
            key={`${item.item_type}-${item.item_id}`}
            className="inline-flex items-center gap-1 px-3 py-1 rounded-full text-sm bg-white border border-[var(--color-primary-100)] shadow-sm"
          >
            <span
              className={`w-1.5 h-1.5 rounded-full ${
                item.item_type === "drug" ? "bg-blue-500" : "bg-emerald-500"
              }`}
            />
            <span className="truncate max-w-[120px]">{item.name}</span>
            <button
              onClick={() => onRemove(item.item_id, item.item_type)}
              className="ml-1 text-gray-400 hover:text-gray-600"
              aria-label={`${item.name} 제거`}
            >
              <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </span>
        ))}
      </div>
    </div>
  );
}
