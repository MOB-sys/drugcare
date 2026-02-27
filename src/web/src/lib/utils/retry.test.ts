import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { withRetry } from "./retry";

beforeEach(() => {
  vi.useFakeTimers();
});

afterEach(() => {
  vi.useRealTimers();
});

describe("withRetry", () => {
  it("returns result on first success", async () => {
    const fn = vi.fn().mockResolvedValue("ok");
    const result = await withRetry(fn);
    expect(result).toBe("ok");
    expect(fn).toHaveBeenCalledTimes(1);
  });

  it("retries on failure then succeeds", async () => {
    const fn = vi.fn()
      .mockRejectedValueOnce(new Error("network"))
      .mockResolvedValueOnce("recovered");

    const promise = withRetry(fn, { baseDelay: 100 });
    await vi.advanceTimersByTimeAsync(100);
    const result = await promise;

    expect(result).toBe("recovered");
    expect(fn).toHaveBeenCalledTimes(2);
  });

  it("throws after max retries exhausted", async () => {
    const fn = vi.fn().mockRejectedValue(new Error("fail"));

    const promise = withRetry(fn, { maxRetries: 1, baseDelay: 50 });
    // Catch to avoid unhandled rejection warning, we'll assert below
    promise.catch(() => {});
    await vi.advanceTimersByTimeAsync(50);

    await expect(promise).rejects.toThrow("fail");
    expect(fn).toHaveBeenCalledTimes(2); // 1 initial + 1 retry
  });

  it("does not retry on 4xx client errors", async () => {
    const err = Object.assign(new Error("not found"), { status: 404 });
    const fn = vi.fn().mockRejectedValue(err);

    await expect(withRetry(fn)).rejects.toThrow("not found");
    expect(fn).toHaveBeenCalledTimes(1);
  });

  it("retries on 5xx server errors", async () => {
    const err = Object.assign(new Error("server"), { status: 500 });
    const fn = vi.fn()
      .mockRejectedValueOnce(err)
      .mockResolvedValueOnce("ok");

    const promise = withRetry(fn, { baseDelay: 100 });
    await vi.advanceTimersByTimeAsync(100);
    const result = await promise;

    expect(result).toBe("ok");
    expect(fn).toHaveBeenCalledTimes(2);
  });

  it("respects maxDelay cap", async () => {
    const fn = vi.fn()
      .mockRejectedValueOnce(new Error("fail"))
      .mockRejectedValueOnce(new Error("fail"))
      .mockResolvedValueOnce("ok");

    const promise = withRetry(fn, { maxRetries: 2, baseDelay: 3000, maxDelay: 5000 });
    // First retry: min(3000 * 2^0, 5000) = 3000
    await vi.advanceTimersByTimeAsync(3000);
    // Second retry: min(3000 * 2^1, 5000) = 5000
    await vi.advanceTimersByTimeAsync(5000);

    const result = await promise;
    expect(result).toBe("ok");
    expect(fn).toHaveBeenCalledTimes(3);
  });
});
