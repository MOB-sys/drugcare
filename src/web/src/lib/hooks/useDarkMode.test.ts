import { renderHook, act } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { useDarkMode } from "./useDarkMode";

const STORAGE_KEY = "pillright_theme";

let store: Record<string, string>;
let mockMatchMedia: { matches: boolean; addEventListener: ReturnType<typeof vi.fn>; removeEventListener: ReturnType<typeof vi.fn> };

beforeEach(() => {
  store = {};
  vi.stubGlobal("localStorage", {
    getItem: (key: string) => store[key] ?? null,
    setItem: (key: string, value: string) => { store[key] = value; },
    removeItem: (key: string) => { delete store[key]; },
  });
  document.documentElement.classList.remove("dark");
  mockMatchMedia = {
    matches: false,
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
  };
  vi.stubGlobal("matchMedia", vi.fn().mockReturnValue(mockMatchMedia));
});

afterEach(() => {
  vi.restoreAllMocks();
});

describe("useDarkMode", () => {
  it("defaults to light theme", () => {
    const { result } = renderHook(() => useDarkMode());
    expect(result.current.theme).toBe("light");
    expect(result.current.isDark).toBe(false);
  });

  it("restores saved theme from localStorage", () => {
    store[STORAGE_KEY] = "dark";
    const { result } = renderHook(() => useDarkMode());
    expect(result.current.theme).toBe("dark");
  });

  it("applies dark class when set to dark", () => {
    const { result } = renderHook(() => useDarkMode());
    act(() => result.current.setTheme("dark"));
    expect(result.current.isDark).toBe(true);
    expect(document.documentElement.classList.contains("dark")).toBe(true);
  });

  it("removes dark class when set to light", () => {
    document.documentElement.classList.add("dark");
    const { result } = renderHook(() => useDarkMode());
    act(() => result.current.setTheme("light"));
    expect(result.current.isDark).toBe(false);
    expect(document.documentElement.classList.contains("dark")).toBe(false);
  });

  it("toggle switches between light and dark", () => {
    const { result } = renderHook(() => useDarkMode());
    act(() => result.current.setTheme("light"));
    expect(result.current.isDark).toBe(false);

    act(() => result.current.toggle());
    expect(result.current.isDark).toBe(true);

    act(() => result.current.toggle());
    expect(result.current.isDark).toBe(false);
  });

  it("persists theme to localStorage", () => {
    const { result } = renderHook(() => useDarkMode());
    act(() => result.current.setTheme("dark"));
    expect(store[STORAGE_KEY]).toBe("dark");
  });

  it("follows system preference when set to system", () => {
    mockMatchMedia.matches = true;
    vi.stubGlobal("matchMedia", vi.fn().mockReturnValue(mockMatchMedia));
    const { result } = renderHook(() => useDarkMode());
    act(() => result.current.setTheme("system"));
    expect(result.current.isDark).toBe(true);
  });
});
