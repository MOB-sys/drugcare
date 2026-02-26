"use client";

import { useState, useEffect } from "react";

const APP_STORE_URL = "https://apps.apple.com/app/yakmeogeo";
const PLAY_STORE_URL = "https://play.google.com/store/apps/details?id=com.yakmeogeo.app";

export function SmartAppBanner() {
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    if (typeof window === "undefined") return;
    const dismissed = sessionStorage.getItem("banner_dismissed");
    if (dismissed) return;
    const isMobile = window.innerWidth < 768;
    if (isMobile) setVisible(true);
  }, []);

  if (!visible) return null;

  function handleDismiss() {
    sessionStorage.setItem("banner_dismissed", "1");
    setVisible(false);
  }

  const storeUrl = /iphone|ipad|ipod/i.test(navigator.userAgent)
    ? APP_STORE_URL
    : PLAY_STORE_URL;

  return (
    <div className="bg-[var(--color-primary)] text-white px-4 py-3 flex items-center gap-3" data-testid="smart-app-banner">
      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium truncate">
          매일 복약 리마인더는 앱에서!
        </p>
        <p className="text-xs text-blue-200 truncate">
          MediCheck 앱으로 복용 시간을 놓치지 마세요
        </p>
      </div>
      <a
        href={storeUrl}
        target="_blank"
        rel="noopener noreferrer"
        className="shrink-0 px-3 py-1.5 rounded-xl bg-white text-[var(--color-primary)] text-sm font-medium hover:bg-[var(--color-primary-50)] transition-colors"
      >
        앱 설치
      </a>
      <button
        onClick={handleDismiss}
        className="shrink-0 p-1 text-blue-200 hover:text-white transition-colors"
        aria-label="배너 닫기"
      >
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>
    </div>
  );
}
