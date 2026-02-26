import { render, screen, cleanup, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi, afterEach, beforeEach } from "vitest";
import { SmartAppBanner } from "./SmartAppBanner";

afterEach(cleanup);

beforeEach(() => {
  sessionStorage.clear();
});

describe("SmartAppBanner", () => {
  it("renders on mobile viewport", () => {
    Object.defineProperty(window, "innerWidth", { value: 375, writable: true });
    render(<SmartAppBanner />);
    expect(screen.getAllByText("매일 복약 리마인더는 앱에서!").length).toBeGreaterThanOrEqual(1);
  });

  it("does not render on desktop viewport", () => {
    Object.defineProperty(window, "innerWidth", { value: 1024, writable: true });
    render(<SmartAppBanner />);
    expect(screen.queryByTestId("smart-app-banner")).toBeNull();
  });

  it("dismisses when X clicked and stores in sessionStorage", () => {
    Object.defineProperty(window, "innerWidth", { value: 375, writable: true });
    render(<SmartAppBanner />);
    fireEvent.click(screen.getByRole("button", { name: /닫기/ }));
    expect(screen.queryByTestId("smart-app-banner")).toBeNull();
    expect(sessionStorage.getItem("banner_dismissed")).toBe("1");
  });

  it("does not render when already dismissed", () => {
    Object.defineProperty(window, "innerWidth", { value: 375, writable: true });
    sessionStorage.setItem("banner_dismissed", "1");
    render(<SmartAppBanner />);
    expect(screen.queryByTestId("smart-app-banner")).toBeNull();
  });
});
