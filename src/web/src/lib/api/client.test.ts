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
  vi.stubEnv("NEXT_PUBLIC_API_URL", "http://test-api:8000");
});

afterEach(() => {
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

  it("throws ApiError on HTTP error", async () => {
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

  it("throws ApiError on 500 server error", async () => {
    global.fetch = mockFetch(
      { success: false, data: null, error: "Internal Server Error", meta: { timestamp: "" } },
      500,
    );

    await expect(fetchApi("/api/v1/broken")).rejects.toThrow(ApiError);
    await expect(fetchApi("/api/v1/broken")).rejects.toMatchObject({
      status: 500,
    });
  });

  it("throws ApiError when success is false", async () => {
    global.fetch = mockFetch({
      success: false,
      data: null,
      error: "비즈니스 로직 에러",
      meta: { timestamp: "" },
    });

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

  it("handles non-JSON error response", async () => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: false,
      status: 502,
      json: () => Promise.reject(new Error("not json")),
    });

    await expect(fetchApi("/api/v1/gateway")).rejects.toThrow(ApiError);
    await expect(fetchApi("/api/v1/gateway")).rejects.toMatchObject({
      status: 502,
      message: "API 오류: 502",
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

  it("handles network failure", async () => {
    global.fetch = vi.fn().mockRejectedValue(new TypeError("Failed to fetch"));

    await expect(fetchApi("/api/v1/test")).rejects.toThrow("Failed to fetch");
  });
});
