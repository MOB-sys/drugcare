import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { fetchApi, ApiError } from "./client";

function mockFetch(body: unknown, status = 200) {
  return vi.fn().mockResolvedValue({
    ok: status >= 200 && status < 300,
    status,
    json: () => Promise.resolve(body),
  });
}

beforeEach(() => {
  vi.useFakeTimers();
  vi.stubEnv("NEXT_PUBLIC_API_URL", "http://test-api:8000");
});

afterEach(() => {
  vi.useRealTimers();
  vi.restoreAllMocks();
});

describe("fetchApi", () => {
  it("returns data on success", async () => {
    global.fetch = mockFetch({
      success: true,
      data: { id: 1, name: "test" },
      error: null,
      meta: { timestamp: "2026-01-01T00:00:00Z" },
    });

    const result = await fetchApi<{ id: number; name: string }>("/api/v1/test");
    expect(result).toEqual({ id: 1, name: "test" });
  });

  it("throws ApiError on 4xx without retry", async () => {
    global.fetch = mockFetch(
      { success: false, data: null, error: "Not Found", meta: { timestamp: "" } },
      404,
    );

    await expect(fetchApi("/api/v1/missing")).rejects.toThrow(ApiError);
    await expect(fetchApi("/api/v1/missing")).rejects.toMatchObject({
      status: 404,
      message: "Not Found",
    });
  });

  it("retries on 5xx then fails", async () => {
    const fn = vi.fn().mockResolvedValue({
      ok: false,
      status: 500,
      json: () => Promise.resolve({
        success: false, data: null, error: "Server Error", meta: { timestamp: "" },
      }),
    });
    global.fetch = fn;

    const promise = fetchApi("/api/v1/broken");
    promise.catch(() => {}); // prevent unhandled rejection
    await vi.advanceTimersByTimeAsync(500);
    await vi.advanceTimersByTimeAsync(1000);

    await expect(promise).rejects.toThrow(ApiError);
    expect(fn).toHaveBeenCalledTimes(3); // 1 initial + 2 retries
  });

  it("throws ApiError when success is false", async () => {
    global.fetch = mockFetch({
      success: false,
      data: null,
      error: "비즈니스 로직 에러",
      meta: { timestamp: "" },
    });

    // success: false with 200 status → 4xx-like (won't retry since ok:true but success:false throws ApiError with status 200, which is < 400)
    // Actually this throws ApiError(200, ...) which is < 400, so no retry
    await expect(fetchApi("/api/v1/logic-error")).rejects.toThrow("비즈니스 로직 에러");
  });

  it("throws ApiError when data is null", async () => {
    global.fetch = mockFetch({
      success: true,
      data: null,
      error: null,
      meta: { timestamp: "" },
    });

    await expect(fetchApi("/api/v1/empty")).rejects.toThrow(ApiError);
  });

  it("handles non-JSON error response (4xx)", async () => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: false,
      status: 400,
      json: () => Promise.reject(new Error("not json")),
    });

    await expect(fetchApi("/api/v1/bad")).rejects.toThrow(ApiError);
    await expect(fetchApi("/api/v1/bad")).rejects.toMatchObject({
      status: 400,
      message: "API 오류: 400",
    });
  });

  it("sends correct headers", async () => {
    global.fetch = mockFetch({
      success: true,
      data: "ok",
      error: null,
      meta: { timestamp: "" },
    });

    await fetchApi("/api/v1/test");

    expect(global.fetch).toHaveBeenCalledWith(
      expect.stringContaining("/api/v1/test"),
      expect.objectContaining({
        credentials: "include",
        headers: expect.objectContaining({
          "Content-Type": "application/json",
        }),
      }),
    );
  });

  it("retries on network failure then recovers", async () => {
    const fn = vi.fn()
      .mockRejectedValueOnce(new TypeError("Failed to fetch"))
      .mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: () => Promise.resolve({
          success: true, data: "recovered", error: null, meta: { timestamp: "" },
        }),
      });
    global.fetch = fn;

    const promise = fetchApi("/api/v1/test");
    await vi.advanceTimersByTimeAsync(500);
    const result = await promise;

    expect(result).toBe("recovered");
    expect(fn).toHaveBeenCalledTimes(2);
  });
});
