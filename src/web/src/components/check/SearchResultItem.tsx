"use client";

import { useState, useRef } from "react";
import { addCabinetItem, deleteCabinetItem } from "@/lib/api/cabinet";
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
  const [cabinetStatus, setCabinetStatus] = useState<"idle" | "added" | "duplicate" | "removing">("idle");
  const cabinetIdRef = useRef<number | null>(null);

  async function handleCabinetAdd(e: React.MouseEvent) {
    e.stopPropagation();
    if (!itemId || cabinetStatus !== "idle") return;
    try {
      const item = await addCabinetItem({ item_type: itemType, item_id: itemId, nickname: name });
      cabinetIdRef.current = item.id;
      setCabinetStatus("added");
    } catch (err) {
      if (err instanceof ApiError && err.status === 409) {
        setCabinetStatus("duplicate");
      }
    }
  }

  async function handleCabinetRemove(e: React.MouseEvent) {
    e.stopPropagation();
    if (cabinetStatus !== "added" || cabinetIdRef.current === null) return;
    setCabinetStatus("removing");
    try {
      await deleteCabinetItem(cabinetIdRef.current);
      cabinetIdRef.current = null;
      setCabinetStatus("idle");
    } catch {
      setCabinetStatus("added");
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
          ? "bg-[var(--color-primary-50)] border-l-4 border-[var(--color-primary)]"
          : disabled
            ? "opacity-50 cursor-not-allowed"
            : "hover:bg-gray-50"
      }`}
    >
      <span
        className={`shrink-0 px-2 py-0.5 rounded-md text-xs font-medium ${
          itemType === "drug"
            ? "bg-blue-50 text-blue-700"
            : "bg-emerald-50 text-emerald-700"
        }`}
      >
        {itemType === "drug" ? "약물" : "영양제"}
      </span>
      <div className="min-w-0 flex-1">
        <p className="font-medium text-gray-900 truncate">{name}</p>
        {sub && <p className="text-sm text-gray-500 truncate">{sub}</p>}
      </div>
      {showCabinetAdd && itemId && (
        cabinetStatus === "added" ? (
          <button
            onClick={handleCabinetRemove}
            className="shrink-0 px-2 py-1 rounded-lg text-xs font-medium bg-emerald-50 text-emerald-600 hover:bg-red-50 hover:text-red-500 transition-colors"
            aria-label={`${name} 복약함에서 제거`}
          >
            ✓ 취소
          </button>
        ) : (
          <button
            onClick={handleCabinetAdd}
            disabled={cabinetStatus !== "idle"}
            className={`shrink-0 px-2 py-1 rounded-lg text-xs font-medium transition-colors ${
              cabinetStatus === "duplicate"
                ? "bg-gray-100 text-gray-400"
                : cabinetStatus === "removing"
                  ? "bg-gray-50 text-gray-400"
                  : "bg-[var(--color-primary-50)] text-[var(--color-primary)] hover:bg-[var(--color-primary-100)]"
            }`}
            aria-label={`${name} 복약함에 추가`}
          >
            {cabinetStatus === "removing" ? "제거 중..." : cabinetStatus === "duplicate" ? "추가됨" : "+복약함"}
          </button>
        )
      )}
      {selected && (
        <svg className="w-5 h-5 text-[var(--color-primary)] shrink-0" fill="currentColor" viewBox="0 0 20 20">
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
