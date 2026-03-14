"use client";

import type { CabinetItem } from "@/types/cabinet";

interface CabinetItemCardProps {
  item: CabinetItem;
  isDeleting?: boolean;
  onDelete: (id: number) => void;
}

export function CabinetItemCard({ item, isDeleting, onDelete }: CabinetItemCardProps) {
  const dateStr = new Date(item.created_at).toLocaleDateString("ko-KR");

  return (
    <div className={`flex items-center gap-3 px-4 py-3 bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 shadow-sm hover:shadow-md transition-all ${isDeleting ? "opacity-50 pointer-events-none" : ""}`}>
      <span
        className={`shrink-0 px-2 py-0.5 rounded-md text-xs font-medium ${
          item.item_type === "drug"
            ? "bg-blue-50 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300"
            : "bg-emerald-50 dark:bg-emerald-900/30 text-emerald-700 dark:text-emerald-300"
        }`}
      >
        {item.item_type === "drug" ? "의약품" : "영양제"}
      </span>
      <div className="min-w-0 flex-1">
        <p className="font-medium text-gray-900 dark:text-gray-100 truncate">
          {item.nickname || item.item_name}
        </p>
        <p className="text-xs text-gray-400 dark:text-gray-500">{dateStr} 추가</p>
      </div>
      <button
        onClick={() => onDelete(item.id)}
        disabled={isDeleting}
        className="shrink-0 p-2.5 rounded-lg text-gray-400 dark:text-gray-500 hover:text-red-500 hover:bg-red-50 transition-colors disabled:opacity-50"
        aria-label={`${item.nickname || item.item_name} 삭제`}
      >
        {isDeleting ? (
          <div className="w-4 h-4 border-2 border-gray-300 dark:border-gray-600 border-t-gray-500 rounded-full animate-spin" role="status" aria-label="삭제 중" />
        ) : (
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        )}
      </button>
    </div>
  );
}
