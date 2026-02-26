"use client";

import { useState } from "react";
import { addCabinetItem } from "@/lib/api/cabinet";
import { ApiError } from "@/lib/api/client";

interface SearchResultItemProps {
  name: string;
  sub: string | null;
  itemType: "drug" | "supplement";
  itemId?: number;
  selected: boolean;
  disabled: boolean;
  onToggle: () => void;
  showCabinetAdd?: boolean;
}

export function SearchResultItem({
  name,
  sub,
  itemType,
  itemId,
  selected,
  disabled,
  onToggle,
  showCabinetAdd = false,
}: SearchResultItemProps) {
  const [cabinetStatus, setCabinetStatus] = useState<"idle" | "added" | "duplicate">("idle");

  async function handleCabinetAdd(e: React.MouseEvent) {
    e.stopPropagation();
    if (!itemId || cabinetStatus !== "idle") return;
    try {
      await addCabinetItem({ item_type: itemType, item_id: itemId, nickname: name });
      setCabinetStatus("added");
    } catch (err) {
      if (err instanceof ApiError && err.status === 409) {
        setCabinetStatus("duplicate");
      }
    }
  }

  return (
    <div
      role="button"
      tabIndex={0}
      onClick={onToggle}
      onKeyDown={(e) => { if (e.key === "Enter" || e.key === " ") onToggle(); }}
      aria-disabled={disabled && !selected}
      className={`w-full text-left px-4 py-3 flex items-center gap-3 transition-colors cursor-pointer ${
        selected
          ? "bg-teal-50 border-l-4 border-[var(--color-brand)]"
          : disabled
            ? "opacity-50 cursor-not-allowed"
            : "hover:bg-gray-50"
      }`}
    >
      <span
        className={`shrink-0 px-2 py-0.5 rounded text-xs font-medium ${
          itemType === "drug"
            ? "bg-blue-100 text-blue-700"
            : "bg-green-100 text-green-700"
        }`}
      >
        {itemType === "drug" ? "약물" : "영양제"}
      </span>
      <div className="min-w-0 flex-1">
        <p className="font-medium text-gray-900 truncate">{name}</p>
        {sub && <p className="text-sm text-gray-500 truncate">{sub}</p>}
      </div>
      {showCabinetAdd && itemId && (
        <button
          onClick={handleCabinetAdd}
          disabled={cabinetStatus !== "idle"}
          className={`shrink-0 px-2 py-1 rounded text-xs font-medium transition-colors ${
            cabinetStatus === "added"
              ? "bg-green-100 text-green-600"
              : cabinetStatus === "duplicate"
                ? "bg-gray-100 text-gray-400"
                : "bg-teal-50 text-[var(--color-brand)] hover:bg-teal-100"
          }`}
          aria-label={`${name} 복약함에 추가`}
        >
          {cabinetStatus === "added" ? "추가됨" : cabinetStatus === "duplicate" ? "추가됨" : "+복약함"}
        </button>
      )}
      {selected && (
        <svg className="w-5 h-5 text-[var(--color-brand)] shrink-0" fill="currentColor" viewBox="0 0 20 20">
          <path
            fillRule="evenodd"
            d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
            clipRule="evenodd"
          />
        </svg>
      )}
    </div>
  );
}
