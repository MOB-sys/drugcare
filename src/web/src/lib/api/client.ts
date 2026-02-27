/** PillRight API 클라이언트 — 서버/클라이언트 양쪽 사용 가능. */

import { withRetry } from "@/lib/utils/retry";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const REQUEST_TIMEOUT = 10_000; // 10초

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
  options?: RequestInit,
): Promise<T> {
  return withRetry(() => fetchApiOnce<T>(path, options));
}

async function fetchApiOnce<T>(
  path: string,
  options?: RequestInit,
): Promise<T> {
  const url = `${API_BASE_URL}${path}`;
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), REQUEST_TIMEOUT);

  try {
    const res = await fetch(url, {
      ...options,
      credentials: "include",
      signal: options?.signal ?? controller.signal,
      headers: {
        "Content-Type": "application/json",
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

    if (!json.success || json.data === null) {
      throw new ApiError(res.status, json.error || "알 수 없는 오류");
    }

    return json.data;
  } catch (error) {
    if (error instanceof DOMException && error.name === "AbortError") {
      throw new ApiError(408, "요청 시간이 초과되었습니다.");
    }
    throw error;
  } finally {
    clearTimeout(timeout);
  }
}
