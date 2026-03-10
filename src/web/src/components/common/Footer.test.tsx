import { render, screen, cleanup } from "@testing-library/react";
import { describe, it, expect, afterEach } from "vitest";
import { Footer } from "./Footer";

afterEach(cleanup);

describe("Footer", () => {
  it("renders disclaimer text", () => {
    render(<Footer />);
    expect(
      screen.getAllByText(/의학적 진단이나 치료를 제공하지 않습니다/).length,
    ).toBeGreaterThanOrEqual(1);
  });

  it("renders copyright", () => {
    render(<Footer />);
    expect(
      screen.getAllByText(/약잘알 \(PillRight\). All rights reserved/).length,
    ).toBeGreaterThanOrEqual(1);
  });
});
