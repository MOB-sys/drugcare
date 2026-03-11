/** API 호출 재시도 유틸리티 — exponential backoff. */

export interface RetryOptions {
  maxRetries?: number;
  baseDelay?: number;
  maxDelay?: number;
  /** 지터 비활성화 (테스트용). */
  disableJitter?: boolean;
}

export async function withRetry<T>(
  fn: () => Promise<T>,
  options: RetryOptions = {},
): Promise<T> {
  const { maxRetries = 2, baseDelay = 500, maxDelay = 5000, disableJitter = false } = options;

  let lastError: unknown;

  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    try {
      return await fn();
    } catch (error) {
      lastError = error;

      // 5xx 서버 에러만 재시도. 4xx 클라이언트 에러, 2xx 비즈니스 로직 에러 등은 재시도 불필요.
      if (
        error instanceof Error &&
        "status" in error &&
        typeof (error as { status: unknown }).status === "number"
      ) {
        const status = (error as { status: number }).status;
        if (status < 500) throw error;
      }

      if (attempt < maxRetries) {
        const jitter = disableJitter ? 1 : Math.random() * 0.3 + 0.85; // 0.85~1.15 범위 지터
        const delay = Math.min(baseDelay * 2 ** attempt * jitter, maxDelay);
        await new Promise((resolve) => setTimeout(resolve, delay));
      }
    }
  }

  throw lastError;
}
