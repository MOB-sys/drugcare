"use client";

import { useEffect, useState } from "react";

interface KakaoShareButtonProps {
  /** 카카오 공유 카드 제목 */
  title: string;
  /** 카카오 공유 카드 설명 */
  description: string;
  /** 공유 카드 이미지 URL (절대 경로) */
  imageUrl?: string;
  /** 공유할 페이지 URL (절대 경로) */
  pageUrl?: string;
  /** 버튼 라벨 텍스트 (기본: "카카오톡 공유") */
  buttonLabel?: string;
  /** 추가 CSS 클래스 */
  className?: string;
}

/**
 * 범용 카카오톡 공유 버튼 컴포넌트.
 *
 * Kakao JS SDK가 layout.tsx에서 로드·초기화된 뒤 활성화되며,
 * SDK가 없거나 초기화되지 않은 경우 자동으로 숨김 처리됩니다.
 */
export function KakaoShareButton({
  title,
  description,
  imageUrl,
  pageUrl,
  buttonLabel = "카카오톡 공유",
  className,
}: KakaoShareButtonProps) {
  const [ready, setReady] = useState(false);

  useEffect(() => {
    /** Kakao SDK가 비동기 로드되므로 폴링으로 초기화 상태를 확인합니다. */
    let attempts = 0;
    const maxAttempts = 20; // 최대 4초 (200ms * 20)
    let timerId: ReturnType<typeof setTimeout> | null = null;

    function check() {
      if (window.Kakao?.isInitialized()) {
        setReady(true);
        return;
      }
      attempts++;
      if (attempts < maxAttempts) {
        timerId = setTimeout(check, 200);
      }
    }

    check();

    return () => {
      if (timerId !== null) clearTimeout(timerId);
    };
  }, []);

  if (!ready) return null;

  function handleShare() {
    try {
      const url = pageUrl || window.location.href;
      const image = imageUrl || `${window.location.origin}/icon-512.png`;

      window.Kakao!.Share.sendDefault({
        objectType: "feed",
        content: {
          title,
          description,
          imageUrl: image,
          link: {
            mobileWebUrl: url,
            webUrl: url,
          },
        },
        buttons: [
          {
            title: "자세히 보기",
            link: {
              mobileWebUrl: url,
              webUrl: url,
            },
          },
        ],
      });
    } catch {
      /* Kakao SDK 호출 실패 — 무시 */
    }
  }

  return (
    <button
      type="button"
      onClick={handleShare}
      className={
        className ??
        "inline-flex items-center gap-1.5 px-4 py-2.5 rounded-xl text-sm font-medium border border-gray-200 dark:border-gray-700 text-gray-600 dark:text-gray-300 hover:bg-[#FEE500] hover:border-[#FEE500] hover:text-[#191919] transition-colors"
      }
      aria-label="카카오톡으로 공유하기"
    >
      {/* 카카오톡 로고 아이콘 */}
      <svg className="w-4 h-4" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
        <path d="M12 3C6.48 3 2 6.36 2 10.44c0 2.61 1.73 4.91 4.33 6.24l-1.1 4.08c-.1.36.3.65.6.44l4.82-3.18c.44.04.89.06 1.35.06 5.52 0 10-3.36 10-7.64C22 6.36 17.52 3 12 3z" />
      </svg>
      {buttonLabel}
    </button>
  );
}
