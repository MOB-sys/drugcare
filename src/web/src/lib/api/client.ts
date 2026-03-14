/** 약잘알 API 클라이언트 — 서버/클라이언트 양쪽 사용 가능. */

import { withRetry } from "@/lib/utils/retry";

// 서버(SSR/SSG): 백엔드 직접 호출, 클라이언트(브라우저): 상대 경로 → Next.js rewrite로 프록시
const API_BASE_URL =
  typeof window === "undefined"
    ? (process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000")
    : "";

const REQUEST_TIMEOUT = 10_000; // 10초
const RATE_LIMIT_MAX = 30; // 엔드포인트 그룹당 최대 요청 수
const RATE_LIMIT_WINDOW = 10_000; // 10초 윈도우

/** 엔드포인트 그룹별 클라이언트 사이드 레이트 리미터. */
const requestLog = new Map<string, number[]>();

function getEndpointGroup(path: string): string {
  const seg = path.split("/").filter(Boolean);
  // /api/v1/drugs/... -> "drugs", /api/v1/interactions/... -> "interactions"
  return seg[2] || "default";
}

async function waitForRateLimit(path: string): Promise<void> {
  if (typeof window === "undefined") return; // skip rate limiting on server
  const group = getEndpointGroup(path);
  const now = Date.now();
  const timestamps = requestLog.get(group) ?? [];

  // 윈도우 밖의 오래된 타임스탬프 제거
  const recent = timestamps.filter((t) => now - t < RATE_LIMIT_WINDOW);

  if (recent.length >= RATE_LIMIT_MAX) {
    const oldest = recent[0];
    const delay = RATE_LIMIT_WINDOW - (now - oldest);
    if (delay > 0) {
      await new Promise((r) => setTimeout(r, delay));
    }
    // 대기 후 가장 오래된 항목 제거하고 윈도우 밖 타임스탬프도 재정리
    const afterWait = Date.now();
    const refreshed = recent.filter((t) => afterWait - t < RATE_LIMIT_WINDOW);
    recent.length = 0;
    recent.push(...refreshed);
  }

  recent.push(now);
  if (recent.length > 0) {
    requestLog.set(group, recent);
  } else {
    requestLog.delete(group);
  }
}

export interface ApiResponse<T> {
  success: boolean;
  data: T | null;
  error: string | null;
  meta: { timestamp: string };
}

export class ApiError extends Error {
  constructor(
    public status: number,
    message: string,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

/** 타입 안전한 API 호출 함수 (타임아웃 + 재시도 포함). */
export async function fetchApi<T>(
  path: string,
  options?: RequestInit & { allowNullData?: boolean },
): Promise<T> {
  // 경로 검증 — 경로 조작(traversal) 및 헤더 인젝션 방지
  if (!path.startsWith('/') || path.includes('..') || /[\r\n]/.test(path)) {
    throw new Error('Invalid API path');
  }

  const method = (options?.method ?? "GET").toUpperCase();
  // POST/PUT/DELETE 등 비멱등 요청은 재시도하지 않음 (중복 생성/삭제 방지)
  if (method !== "GET" && method !== "HEAD") {
    return fetchApiOnce<T>(path, options);
  }
  return withRetry(() => fetchApiOnce<T>(path, options));
}

async function fetchApiOnce<T>(
  path: string,
  options?: RequestInit & { allowNullData?: boolean },
): Promise<T> {
  await waitForRateLimit(path);
  const url = `${API_BASE_URL}${path}`;
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), REQUEST_TIMEOUT);

  // caller signal과 timeout signal을 합성 (AbortSignal.any 대신 수동 합성 — Node 18 호환)
  if (options?.signal) {
    const callerSignal = options.signal;
    if (callerSignal.aborted) {
      controller.abort(callerSignal.reason);
    } else {
      callerSignal.addEventListener("abort", () => controller.abort(callerSignal.reason), { once: true });
    }
  }
  const composedSignal = controller.signal;

  try {
    const res = await fetch(url, {
      ...options,
      credentials: "include",
      signal: composedSignal,
      headers: {
        "Content-Type": "application/json",
        // SSR에서 POST 요청 시 CSRF 검증 통과를 위해 Origin 헤더 추가
        ...(typeof window === "undefined" && { Origin: process.env.NEXT_PUBLIC_SITE_URL || "https://pillright.com" }),
        ...options?.headers,
      },
    });

    if (!res.ok) {
      const body = await res.json().catch(() => null);
      throw new ApiError(
        res.status,
        body?.error || `API 오류: ${res.status}`,
      );
    }

    const json: ApiResponse<T> = await res.json();

    if (!json.success) {
      throw new ApiError(res.status, json.error || "알 수 없는 오류");
    }

    // DELETE 등 응답 본문이 없는 경우 allowNullData 옵션으로 null 허용
    if (json.data === null && !options?.allowNullData) {
      throw new ApiError(res.status, json.error || "알 수 없는 오류");
    }

    return json.data as T;
  } catch (error) {
    if (
      (typeof DOMException !== "undefined" && error instanceof DOMException && error.name === "AbortError") ||
      (error instanceof Error && error.name === "AbortError")
    ) {
      throw new ApiError(408, "요청 시간이 초과되었습니다.");
    }
    throw error;
  } finally {
    clearTimeout(timeout);
  }
}
