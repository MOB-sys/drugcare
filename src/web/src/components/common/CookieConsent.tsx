"use client";

import { useState, useEffect } from "react";

const STORAGE_KEY = "cookie-consent";

type ConsentValue = "all" | "essential" | null;

function getConsent(): ConsentValue {
  if (typeof window === "undefined") return null;
  const v = localStorage.getItem(STORAGE_KEY);
  if (v === "all" || v === "essential") return v;
  return null;
}

/**
 * GA4/AdSense 쿠키 동의 배너.
 * - "동의": cookie-consent = "all" → GA4/AdSense 정상 로드
 * - "필수만 허용": cookie-consent = "essential" → GA4/AdSense 비활성화
 */
export function CookieConsent() {
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    if (getConsent() === null) {
      setVisible(true);
    }
  }, []);

  function handleAccept(value: "all" | "essential") {
    localStorage.setItem(STORAGE_KEY, value);
    setVisible(false);

    if (value === "essential") {
      // GA4 옵트아웃: google analytics 공식 비활성화 프로퍼티
      const gaId = process.env.NEXT_PUBLIC_GA_ID;
      if (gaId) {
        (window as unknown as Record<string, boolean>)[`ga-disable-${gaId}`] = true;
      }
      // AdSense 비활성화 — 이미 로드된 광고 숨김
      document.querySelectorAll("ins.adsbygoogle").forEach((el) => {
        (el as HTMLElement).style.display = "none";
      });
    }
  }

  if (!visible) return null;

  return (
    <div
      role="dialog"
      aria-label="쿠키 동의"
      className="fixed bottom-0 left-0 right-0 z-50 border-t border-gray-200 bg-white/95 backdrop-blur-sm px-4 py-3 shadow-[0_-2px_10px_rgba(0,0,0,0.08)] dark:border-gray-700 dark:bg-gray-900/95"
    >
      <div className="mx-auto flex max-w-3xl flex-col items-center gap-3 sm:flex-row sm:justify-between">
        <p className="text-center text-sm text-gray-600 dark:text-gray-300 sm:text-left">
          원활한 서비스 제공을 위해 분석(GA4) 및 광고(AdSense) 쿠키를 사용합니다.
        </p>
        <div className="flex shrink-0 gap-2">
          <button
            onClick={() => handleAccept("essential")}
            className="rounded-lg border border-gray-300 px-4 py-1.5 text-sm text-gray-600 transition-colors hover:bg-gray-100 dark:border-gray-600 dark:text-gray-300 dark:hover:bg-gray-800"
          >
            필수만 허용
          </button>
          <button
            onClick={() => handleAccept("all")}
            className="rounded-lg bg-[var(--color-primary)] px-4 py-1.5 text-sm font-medium text-white transition-colors hover:opacity-90"
          >
            동의
          </button>
        </div>
      </div>
    </div>
  );
}
