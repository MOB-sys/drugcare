/** API 호출 재시도 유틸리티 — exponential backoff. */

export interface RetryOptions {
  maxRetries?: number;
  baseDelay?: number;
  maxDelay?: number;
}

export async function withRetry<T>(
  fn: () => Promise<T>,
  options: RetryOptions = {},
): Promise<T> {
  const { maxRetries = 2, baseDelay = 500, maxDelay = 5000 } = options;

  let lastError: unknown;

  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    try {
      return await fn();
    } catch (error) {
      lastError = error;

      // 4xx 클라이언트 에러 또는 비즈니스 로직 에러는 재시도하지 않음
      if (
        error instanceof Error &&
        "status" in error &&
        typeof (error as Record<string, unknown>).status === "number"
      ) {
        const status = (error as Record<string, unknown>).status as number;
        if (status < 500 && status !== 0) throw error;
      }

      if (attempt < maxRetries) {
        const delay = Math.min(baseDelay * 2 ** attempt, maxDelay);
        await new Promise((resolve) => setTimeout(resolve, delay));
      }
    }
  }

  throw lastError;
}
