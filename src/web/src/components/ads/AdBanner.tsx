"use client";

import { useEffect, useRef, useState } from "react";

interface AdBannerProps {
  slot: string;
  format?: "auto" | "rectangle" | "horizontal";
  className?: string;
}

declare global {
  interface Window {
    adsbygoogle: unknown[];
  }
}

export function AdBanner({ slot, format = "auto", className = "" }: AdBannerProps) {
  const adsenseId = process.env.NEXT_PUBLIC_ADSENSE_ID;
  const pushed = useRef(false);
  const containerRef = useRef<HTMLDivElement>(null);
  const [filled, setFilled] = useState(false);

  useEffect(() => {
    if (!adsenseId || pushed.current) return;
    try {
      (window.adsbygoogle = window.adsbygoogle || []).push({});
      pushed.current = true;
    } catch {
      /* AdSense not loaded */
    }
  }, [adsenseId]);

  // 광고가 실제로 채워졌는지 감시 — 승인 전이면 숨김
  useEffect(() => {
    if (!adsenseId || !containerRef.current) return;
    const ins = containerRef.current.querySelector("ins.adsbygoogle");
    if (!ins) return;

    const observer = new MutationObserver(() => {
      const hasContent = ins.getAttribute("data-ad-status") === "filled"
        || ins.childElementCount > 0;
      setFilled(hasContent);
    });
    observer.observe(ins, { attributes: true, childList: true, subtree: true });

    // 초기 체크
    const hasContent = ins.getAttribute("data-ad-status") === "filled"
      || ins.childElementCount > 0;
    if (hasContent) setFilled(true);

    return () => observer.disconnect();
  }, [adsenseId]);

  if (!adsenseId) {
    return null;
  }

  return (
    <div
      ref={containerRef}
      className={`ad-banner my-6 ${className} ${filled ? "" : "hidden"}`.trim()}
    >
      <ins
        className="adsbygoogle"
        style={{ display: "block" }}
        data-ad-client={adsenseId}
        data-ad-slot={slot}
        data-ad-format={format}
        data-full-width-responsive="true"
      />
    </div>
  );
}
