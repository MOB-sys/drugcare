"use client";

import { useState } from "react";

declare global {
  interface Window {
    Kakao?: {
      isInitialized(): boolean;
      Share: {
        sendDefault(params: Record<string, unknown>): void;
      };
    };
  }
}

export function ShareActions() {
  const [copied, setCopied] = useState(false);

  async function handleCopyLink() {
    try {
      await navigator.clipboard.writeText(window.location.href);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch { /* clipboard not available */ }
  }

  async function handleShare() {
    if (navigator.share) {
      try {
        await navigator.share({
          title: document.title,
          url: window.location.href,
        });
      } catch { /* user cancelled */ }
    } else {
      handleCopyLink();
    }
  }

  function handlePrint() {
    window.print();
  }

  function handleKakaoShare() {
    try {
      if (!window.Kakao?.isInitialized()) return;
      window.Kakao.Share.sendDefault({
        objectType: "feed",
        content: {
          title: document.title,
          description: "PillRight — 약/영양제 상호작용 체커",
          imageUrl: `${window.location.origin}/icon-512`,
          link: { mobileWebUrl: window.location.href, webUrl: window.location.href },
        },
        buttons: [
          { title: "확인하기", link: { mobileWebUrl: window.location.href, webUrl: window.location.href } },
        ],
      });
    } catch { /* Kakao SDK not loaded */ }
  }

  const kakaoAvailable = typeof window !== "undefined" && window.Kakao?.isInitialized();

  return (
    <div className="flex flex-wrap gap-2">
      {/* URL 복사 */}
      <button
        onClick={handleCopyLink}
        className="flex items-center gap-1.5 px-3 py-2 rounded-xl text-sm font-medium border border-gray-200 text-gray-600 hover:bg-gray-50 transition-colors"
      >
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 5H6a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2v-1M8 5a2 2 0 002 2h2a2 2 0 002-2M8 5a2 2 0 012-2h2a2 2 0 012 2m0 0h2a2 2 0 012 2v3m2 4H10m0 0l3-3m-3 3l3 3" />
        </svg>
        {copied ? "복사됨!" : "링크 복사"}
      </button>

      {/* 카카오톡 공유 */}
      {kakaoAvailable && (
        <button
          onClick={handleKakaoShare}
          className="flex items-center gap-1.5 px-3 py-2 rounded-xl text-sm font-medium border border-gray-200 text-gray-600 hover:bg-[#FEE500] hover:border-[#FEE500] hover:text-[#191919] transition-colors"
        >
          <svg className="w-4 h-4" viewBox="0 0 24 24" fill="currentColor">
            <path d="M12 3C6.48 3 2 6.36 2 10.44c0 2.61 1.73 4.91 4.33 6.24l-1.1 4.08c-.1.36.3.65.6.44l4.82-3.18c.44.04.89.06 1.35.06 5.52 0 10-3.36 10-7.64C22 6.36 17.52 3 12 3z" />
          </svg>
          카카오톡
        </button>
      )}

      {/* 공유 */}
      <button
        onClick={handleShare}
        className="flex items-center gap-1.5 px-3 py-2 rounded-xl text-sm font-medium border border-gray-200 text-gray-600 hover:bg-gray-50 transition-colors"
      >
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z" />
        </svg>
        공유
      </button>

      {/* 인쇄 */}
      <button
        onClick={handlePrint}
        className="flex items-center gap-1.5 px-3 py-2 rounded-xl text-sm font-medium border border-gray-200 text-gray-600 hover:bg-gray-50 transition-colors"
      >
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z" />
        </svg>
        인쇄
      </button>
    </div>
  );
}
