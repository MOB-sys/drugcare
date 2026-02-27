import { renderHook, act } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { useToast } from "./useToast";

beforeEach(() => {
  vi.useFakeTimers();
});

afterEach(() => {
  vi.useRealTimers();
});

describe("useToast", () => {
  it("starts with empty toasts", () => {
    const { result } = renderHook(() => useToast());
    expect(result.current.toasts).toEqual([]);
  });

  it("adds a toast", () => {
    const { result } = renderHook(() => useToast());
    act(() => result.current.addToast("Hello", "success"));
    expect(result.current.toasts).toHaveLength(1);
    expect(result.current.toasts[0].message).toBe("Hello");
    expect(result.current.toasts[0].type).toBe("success");
  });

  it("defaults to info type", () => {
    const { result } = renderHook(() => useToast());
    act(() => result.current.addToast("Info message"));
    expect(result.current.toasts[0].type).toBe("info");
  });

  it("removes a toast by id", () => {
    const { result } = renderHook(() => useToast());
    act(() => result.current.addToast("A", "success"));
    const id = result.current.toasts[0].id;
    act(() => result.current.removeToast(id));
    expect(result.current.toasts).toHaveLength(0);
  });

  it("auto-dismisses after 3.5 seconds", () => {
    const { result } = renderHook(() => useToast());
    act(() => result.current.addToast("Temp", "warning"));
    expect(result.current.toasts).toHaveLength(1);
    act(() => vi.advanceTimersByTime(3500));
    expect(result.current.toasts).toHaveLength(0);
  });

  it("limits to 5 toasts max", () => {
    const { result } = renderHook(() => useToast());
    act(() => {
      for (let i = 0; i < 7; i++) {
        result.current.addToast(`Toast ${i}`);
      }
    });
    expect(result.current.toasts.length).toBeLessThanOrEqual(5);
  });
});
