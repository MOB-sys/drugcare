import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { track } from "./track";

// localStorage mock for test isolation
const store: Record<string, string> = {};
const localStorageMock = {
  getItem: (key: string) => store[key] ?? null,
  setItem: (key: string, value: string) => { store[key] = value; },
  removeItem: (key: string) => { delete store[key]; },
  clear: () => { Object.keys(store).forEach((k) => delete store[k]); },
  get length() { return Object.keys(store).length; },
  key: (i: number) => Object.keys(store)[i] ?? null,
};

describe("track", () => {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  let fetchSpy: any;
  const mockGtag = vi.fn();

  beforeEach(() => {
    Object.defineProperty(window, "localStorage", { value: localStorageMock, writable: true });
    window.gtag = mockGtag;
    fetchSpy = vi.spyOn(globalThis, "fetch").mockResolvedValue(new Response());
    localStorageMock.clear();
  });

  afterEach(() => {
    mockGtag.mockClear();
    fetchSpy.mockRestore();
    localStorageMock.clear();
  });

  it("sends event to GA4 and backend", () => {
    track("search", { query: "타이레놀", filter: "all", result_count: 5 });

    expect(mockGtag).toHaveBeenCalledWith("event", "search", {
      query: "타이레놀",
      filter: "all",
      result_count: 5,
    });

    expect(fetchSpy).toHaveBeenCalledWith("/api/v1/metrics/event", expect.objectContaining({
      method: "POST",
      credentials: "include",
    }));

    const body = JSON.parse((fetchSpy.mock.calls[0][1] as RequestInit).body as string);
    expect(body.event_type).toBe("search");
    expect(body.event_data.query).toBe("타이레놀");
  });

  it("skips GA4 when cookie consent is essential", () => {
    localStorageMock.setItem("cookie-consent", "essential");

    track("detail_view", { type: "drug", id: 1, name: "타이레놀" });

    expect(mockGtag).not.toHaveBeenCalled();
    expect(fetchSpy).toHaveBeenCalled();
  });

  it("does not throw when fetch fails", () => {
    fetchSpy.mockRejectedValueOnce(new Error("network error"));
    expect(() => track("cabinet_add", { type: "drug", id: 1, name: "test" })).not.toThrow();
  });
});
