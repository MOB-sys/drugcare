"use client";

import { getStoreUrlForPlatform } from "@/lib/constants/appStore";

export function AppPromotionCTA() {
  const storeUrl = getStoreUrlForPlatform("result-cta");

  return (
    <div
      className="rounded-xl border border-[var(--color-primary-100)] bg-[var(--color-primary-50)] p-4 text-center"
      data-testid="app-promotion-cta"
    >
      <p className="text-sm font-semibold text-[var(--color-primary)] mb-1">
        이 결과를 앱에서 저장하고 관리하세요
      </p>
      <p className="text-xs text-gray-500 mb-3">
        푸시 리마인더로 복용 시간도 놓치지 마세요
      </p>
      <a
        href={storeUrl}
        target="_blank"
        rel="noopener noreferrer"
        className="inline-block px-5 py-2 rounded-xl text-white text-sm font-semibold bg-[var(--color-primary)] hover:bg-[var(--color-primary-dark)] shadow-md transition-all"
      >
        앱 다운로드
      </a>
    </div>
  );
}
