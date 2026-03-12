"use client";

import { useEffect, useRef } from "react";
import { track } from "@/lib/analytics/track";

interface Props {
  type: "drug" | "supplement" | "food" | "herbal";
  id: number;
  name: string;
}

/** SSG/SSR 상세 페이지에서 클라이언트 사이드 detail_view 이벤트를 전송한다. */
export function DetailViewTracker({ type, id, name }: Props) {
  const sent = useRef(false);

  useEffect(() => {
    if (sent.current) return;
    sent.current = true;
    track("detail_view", { type, id, name });
  }, [type, id, name]);

  return null;
}
