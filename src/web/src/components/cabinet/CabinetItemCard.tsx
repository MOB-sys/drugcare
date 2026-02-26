"use client";

import type { CabinetItem } from "@/types/cabinet";

interface CabinetItemCardProps {
  item: CabinetItem;
  onDelete: (id: number) => void;
}

export function CabinetItemCard({ item, onDelete }: CabinetItemCardProps) {
  const dateStr = new Date(item.created_at).toLocaleDateString("ko-KR");

  return (
    <div className="flex items-center gap-3 px-4 py-3 bg-white rounded-lg border border-gray-200">
      <span
        className={`shrink-0 px-2 py-0.5 rounded text-xs font-medium ${
          item.item_type === "drug"
            ? "bg-blue-100 text-blue-700"
            : "bg-green-100 text-green-700"
        }`}
      >
        {item.item_type === "drug" ? "의약품" : "영양제"}
      </span>
      <div className="min-w-0 flex-1">
        <p className="font-medium text-gray-900 truncate">
          {item.nickname || item.item_name}
        </p>
        <p className="text-xs text-gray-400">{dateStr} 추가</p>
      </div>
      <button
        onClick={() => onDelete(item.id)}
        className="shrink-0 p-1.5 rounded-md text-gray-400 hover:text-red-500 hover:bg-red-50 transition-colors"
        aria-label={`${item.nickname || item.item_name} 삭제`}
      >
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>
    </div>
  );
}
