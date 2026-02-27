import { renderHook, act } from "@testing-library/react";
import { describe, it, expect, beforeEach, afterEach, vi } from "vitest";
import { useRecentSearches } from "./useRecentSearches";

const STORAGE_KEY = "pillright_recent_searches";

let store: Record<string, string>;

beforeEach(() => {
  store = {};
  vi.stubGlobal("localStorage", {
    getItem: (key: string) => store[key] ?? null,
    setItem: (key: string, value: string) => { store[key] = value; },
    removeItem: (key: string) => { delete store[key]; },
  });
});

afterEach(() => {
  vi.restoreAllMocks();
});

describe("useRecentSearches", () => {
  it("starts with empty list", () => {
    const { result } = renderHook(() => useRecentSearches());
    expect(result.current.recentSearches).toEqual([]);
  });

  it("loads saved searches from localStorage", () => {
    store[STORAGE_KEY] = JSON.stringify(["타이레놀", "오메가3"]);
    const { result } = renderHook(() => useRecentSearches());
    expect(result.current.recentSearches).toEqual(["타이레놀", "오메가3"]);
  });

  it("adds a search and persists", () => {
    const { result } = renderHook(() => useRecentSearches());
    act(() => result.current.addSearch("비타민D"));
    expect(result.current.recentSearches).toEqual(["비타민D"]);
    expect(JSON.parse(store[STORAGE_KEY])).toEqual(["비타민D"]);
  });

  it("moves duplicate to front", () => {
    const { result } = renderHook(() => useRecentSearches());
    act(() => result.current.addSearch("A"));
    act(() => result.current.addSearch("B"));
    act(() => result.current.addSearch("A"));
    expect(result.current.recentSearches).toEqual(["A", "B"]);
  });

  it("limits to 8 items", () => {
    const { result } = renderHook(() => useRecentSearches());
    for (let i = 0; i < 10; i++) {
      act(() => result.current.addSearch(`search-${i}`));
    }
    expect(result.current.recentSearches).toHaveLength(8);
    expect(result.current.recentSearches[0]).toBe("search-9");
  });

  it("ignores empty/whitespace queries", () => {
    const { result } = renderHook(() => useRecentSearches());
    act(() => result.current.addSearch(""));
    act(() => result.current.addSearch("   "));
    expect(result.current.recentSearches).toEqual([]);
  });

  it("removes a specific search", () => {
    const { result } = renderHook(() => useRecentSearches());
    act(() => result.current.addSearch("A"));
    act(() => result.current.addSearch("B"));
    act(() => result.current.removeSearch("A"));
    expect(result.current.recentSearches).toEqual(["B"]);
  });

  it("clears all searches", () => {
    const { result } = renderHook(() => useRecentSearches());
    act(() => result.current.addSearch("A"));
    act(() => result.current.addSearch("B"));
    act(() => result.current.clearAll());
    expect(result.current.recentSearches).toEqual([]);
    expect(store[STORAGE_KEY]).toBeUndefined();
  });
});
