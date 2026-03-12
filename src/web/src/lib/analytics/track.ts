/** GA4 + 백엔드 메트릭스 이중 전송 유틸리티. */

type ItemType = "drug" | "supplement" | "food" | "herbal";

interface EventMap {
  search: { query: string; filter: string; result_count: number };
  interaction_check: { item_count: number; items: string };
  interaction_result: { total_checked: number; interactions_found: number; has_danger: boolean };
  detail_view: { type: ItemType; id: number; name: string };
  cabinet_add: { type: ItemType; id: number; name: string };
  cabinet_remove: { id: number };
  share_click: { method: "copy" | "kakao" | "native" | "print" };
  app_cta_click: { source: string };
  compare_select: { slot: "a" | "b"; type: ItemType; id: number; name: string };
  filter_change: { filter: string };
}

/** GA4로 이벤트 전송 (쿠키 동의 확인). */
function sendToGA4<K extends keyof EventMap>(event: K, params: EventMap[K]) {
  if (typeof window === "undefined") return;
  if (typeof window.gtag !== "function") return;

  // 쿠키 동의 확인 — "essential"이면 GA4 비활성화 상태
  const consent = localStorage.getItem("cookie-consent");
  if (consent === "essential") return;

  window.gtag("event", event, params as Record<string, unknown>);
}

/** 백엔드 /api/v1/metrics/event 로 전송 (fire-and-forget). */
function sendToBackend<K extends keyof EventMap>(event: K, params: EventMap[K]) {
  if (typeof window === "undefined") return;

  fetch("/api/v1/metrics/event", {
    method: "POST",
    credentials: "include",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      event_type: event,
      event_data: params,
    }),
  }).catch(() => {
    // fire-and-forget: 실패해도 무시
  });
}

/** 이벤트를 GA4 + 백엔드 양쪽으로 전송한다. */
export function track<K extends keyof EventMap>(event: K, params: EventMap[K]) {
  sendToGA4(event, params);
  sendToBackend(event, params);
}
