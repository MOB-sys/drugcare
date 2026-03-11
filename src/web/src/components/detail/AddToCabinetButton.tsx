"use client";

import { useState, useRef } from "react";
import { addCabinetItem, deleteCabinetItem } from "@/lib/api/cabinet";
import { ApiError } from "@/lib/api/client";
import { useToastContext } from "@/components/common/ToastProvider";

interface AddToCabinetButtonProps {
  itemType: "drug" | "supplement" | "food" | "herbal";
  itemId: number;
  itemName: string;
}

export function AddToCabinetButton({
  itemType,
  itemId,
  itemName,
}: AddToCabinetButtonProps) {
  const [status, setStatus] = useState<"idle" | "loading" | "added" | "removing" | "duplicate">("idle");
  const cabinetIdRef = useRef<number | null>(null);
  const { addToast } = useToastContext();

  async function handleAdd() {
    if (status !== "idle") return;
    setStatus("loading");
    try {
      const item = await addCabinetItem({ item_type: itemType, item_id: itemId, nickname: itemName });
      cabinetIdRef.current = item.id;
      setStatus("added");
      addToast(`${itemName}을(를) 복약함에 추가했습니다.`, "success");
    } catch (e) {
      if (e instanceof ApiError && e.status === 409) {
        setStatus("duplicate");
        addToast("이미 복약함에 추가된 항목입니다.", "info");
      } else {
        setStatus("idle");
        addToast("복약함 추가에 실패했습니다. 다시 시도해주세요.", "error");
      }
    }
  }

  async function handleRemove() {
    if (status !== "added" || cabinetIdRef.current === null) return;
    setStatus("removing");
    try {
      await deleteCabinetItem(cabinetIdRef.current);
      cabinetIdRef.current = null;
      setStatus("idle");
      addToast(`${itemName}을(를) 복약함에서 제거했습니다.`, "info");
    } catch {
      setStatus("added");
      addToast("제거에 실패했습니다. 다시 시도해주세요.", "error");
    }
  }

  return (
    <div className="inline-flex items-center gap-2">
      {status === "added" ? (
        <>
          <span className="inline-flex items-center gap-1.5 px-4 py-2.5 rounded-xl text-sm font-medium bg-emerald-50 text-emerald-700 border border-emerald-200">
            <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
              <path
                fillRule="evenodd"
                d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                clipRule="evenodd"
              />
            </svg>
            추가됨
          </span>
          <button
            onClick={handleRemove}
            className="inline-flex items-center gap-1 px-3 py-2.5 rounded-xl text-sm font-medium text-red-600 border border-red-200 bg-white dark:bg-gray-900 hover:bg-red-50 active:scale-[0.98] transition-all"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
            취소
          </button>
        </>
      ) : (
        <button
          onClick={handleAdd}
          disabled={status !== "idle"}
          className={`inline-flex items-center gap-1.5 px-4 py-2.5 rounded-xl text-sm font-medium transition-all ${
            status === "duplicate"
              ? "bg-gray-100 dark:bg-gray-800 text-gray-500 dark:text-gray-400 border border-gray-200 dark:border-gray-700"
              : status === "loading" || status === "removing"
                ? "bg-gray-50 dark:bg-gray-800 text-gray-400 dark:text-gray-500 border border-gray-200 dark:border-gray-700"
                : "bg-white dark:bg-gray-900 text-[var(--color-primary)] border border-[var(--color-primary)] hover:bg-[var(--color-primary-50)] active:scale-[0.98]"
          }`}
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
          </svg>
          {status === "loading" ? "추가 중..." : status === "removing" ? "제거 중..." : status === "duplicate" ? "이미 추가됨" : "복약함에 추가"}
        </button>
      )}
    </div>
  );
}
