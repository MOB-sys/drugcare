"use client";

import { useState } from "react";
import { addCabinetItem } from "@/lib/api/cabinet";
import { ApiError } from "@/lib/api/client";

interface AddToCabinetButtonProps {
  itemType: "drug" | "supplement";
  itemId: number;
  itemName: string;
}

export function AddToCabinetButton({
  itemType,
  itemId,
  itemName,
}: AddToCabinetButtonProps) {
  const [status, setStatus] = useState<"idle" | "loading" | "added" | "duplicate">("idle");

  async function handleClick() {
    if (status === "added" || status === "duplicate" || status === "loading") return;
    setStatus("loading");
    try {
      await addCabinetItem({ item_type: itemType, item_id: itemId, nickname: itemName });
      setStatus("added");
    } catch (e) {
      if (e instanceof ApiError && e.status === 409) {
        setStatus("duplicate");
      } else {
        setStatus("idle");
      }
    }
  }

  const label =
    status === "added"
      ? "추가됨!"
      : status === "duplicate"
        ? "이미 추가됨"
        : status === "loading"
          ? "추가 중..."
          : "복약함에 추가";

  const isDisabled = status !== "idle";

  return (
    <button
      onClick={handleClick}
      disabled={isDisabled}
      className={`inline-flex items-center gap-1.5 px-4 py-2.5 rounded-lg text-sm font-medium transition-colors ${
        status === "added"
          ? "bg-green-50 text-green-700 border border-green-200"
          : status === "duplicate"
            ? "bg-gray-100 text-gray-500 border border-gray-200"
            : "bg-white text-[var(--color-brand)] border border-[var(--color-brand)] hover:bg-teal-50"
      }`}
    >
      {status === "added" ? (
        <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
          <path
            fillRule="evenodd"
            d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
            clipRule="evenodd"
          />
        </svg>
      ) : (
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
        </svg>
      )}
      {label}
    </button>
  );
}
