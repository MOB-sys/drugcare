/** 약잘알 Service Worker — 오프라인 지원 + 정적 자산 캐싱 */

const CACHE_VERSION = "3";
const CACHE_NAME = `pillright-v${CACHE_VERSION}`;
const OFFLINE_URL = "/offline";

const PRECACHE_ASSETS = [OFFLINE_URL];

/* Install — 오프라인 페이지 프리캐시 */
self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(PRECACHE_ASSETS)),
  );
  self.skipWaiting();
});

/* Activate — 이전 캐시 정리 */
self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(
        keys
          .filter((key) => key.startsWith("pillright-") && key !== CACHE_NAME)
          .map((key) => caches.delete(key)),
      ),
    ),
  );
  self.clients.claim();
});

/* Fetch — 네트워크 우선, 실패 시 캐시/오프라인 폴백 */
self.addEventListener("fetch", (event) => {
  const { request } = event;

  /* 외부 도메인 및 API 호출은 SW가 관여하지 않음 */
  const url = new URL(request.url);
  if (url.origin !== self.location.origin) return;
  if (request.url.includes("/api/")) return;

  /* Navigation (HTML) — 네트워크 우선, 실패 시 오프라인 페이지 */
  if (request.mode === "navigate") {
    event.respondWith(
      fetch(request).catch(() => caches.match(OFFLINE_URL)),
    );
    return;
  }

  /* 정적 자산 (JS, CSS, 이미지, 폰트) — 캐시 우선 */
  if (
    request.destination === "script" ||
    request.destination === "style" ||
    request.destination === "image" ||
    request.destination === "font"
  ) {
    event.respondWith(
      caches.match(request).then(
        (cached) =>
          cached ||
          fetch(request).then((response) => {
            const clone = response.clone();
            caches.open(CACHE_NAME).then((cache) => cache.put(request, clone));
            return response;
          }),
      ),
    );
    return;
  }
});
