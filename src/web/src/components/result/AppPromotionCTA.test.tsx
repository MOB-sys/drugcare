import { render, screen, cleanup } from "@testing-library/react";
import { describe, it, expect, afterEach } from "vitest";
import { AppPromotionCTA } from "./AppPromotionCTA";

afterEach(cleanup);

describe("AppPromotionCTA", () => {
  it("renders promotion text", () => {
    render(<AppPromotionCTA />);
    expect(
      screen.getAllByText("이 결과를 앱에서 저장하고 관리하세요").length,
    ).toBeGreaterThanOrEqual(1);
  });

  it("renders download link", () => {
    render(<AppPromotionCTA />);
    const link = screen.getByRole("link", { name: "앱 다운로드" });
    expect(link).toBeDefined();
    expect(link.getAttribute("target")).toBe("_blank");
  });

  it("has correct test id", () => {
    render(<AppPromotionCTA />);
    expect(screen.getByTestId("app-promotion-cta")).toBeDefined();
  });
});
