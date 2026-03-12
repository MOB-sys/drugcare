"use client";

import { useEffect, useRef } from "react";
import { track } from "@/lib/analytics/track";

interface Props {
  totalChecked: number;
  interactionsFound: number;
  hasDanger: boolean;
}

/** 결과 페이지(SSR) 로드 시 클라이언트에서 이벤트를 전송한다. */
export function ResultTracker({ totalChecked, interactionsFound, hasDanger }: Props) {
  const sent = useRef(false);

  useEffect(() => {
    if (sent.current) return;
    sent.current = true;
    track("interaction_result", {
      total_checked: totalChecked,
      interactions_found: interactionsFound,
      has_danger: hasDanger,
    });
  }, [totalChecked, interactionsFound, hasDanger]);

  return null;
}
