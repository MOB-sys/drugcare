import { render, screen, cleanup } from "@testing-library/react";
import { describe, it, expect, afterEach } from "vitest";
import { DisclaimerBanner } from "./DisclaimerBanner";

afterEach(cleanup);

describe("DisclaimerBanner", () => {
  it("renders disclaimer message", () => {
    render(<DisclaimerBanner />);
    expect(
      screen.getAllByText(/의사\/약사의 전문적 판단을 대체하지 않습니다/).length,
    ).toBeGreaterThanOrEqual(1);
  });
});
