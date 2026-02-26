"use client";

import { MIN_INTERACTION_ITEMS } from "@/lib/constants/severity";
import type { SelectedItem } from "@/types/search";

interface CheckButtonProps {
  items: SelectedItem[];
  isLoading: boolean;
  onClick: () => void;
}

export function CheckButton({ items, isLoading, onClick }: CheckButtonProps) {
  const canCheck = items.length >= MIN_INTERACTION_ITEMS && !isLoading;

  return (
    <button
      onClick={onClick}
      disabled={!canCheck}
      className={`w-full py-3 rounded-lg text-white font-semibold text-base transition-colors ${
        canCheck
          ? "bg-[var(--color-brand)] hover:bg-[var(--color-brand-dark)]"
          : "bg-gray-300 cursor-not-allowed"
      }`}
    >
      {isLoading
        ? "확인 중..."
        : items.length < MIN_INTERACTION_ITEMS
          ? `${MIN_INTERACTION_ITEMS}개 이상 선택하세요`
          : `상호작용 확인 (${items.length}개)`}
    </button>
  );
}
