import { render, screen, cleanup } from "@testing-library/react";
import { describe, it, expect, afterEach } from "vitest";
import { EmptyState } from "./EmptyState";

afterEach(cleanup);

describe("EmptyState", () => {
  it("renders empty message", () => {
    render(<EmptyState />);
    expect(screen.getAllByText("복약함이 비어 있습니다").length).toBeGreaterThanOrEqual(1);
  });

  it("links to /check page", () => {
    render(<EmptyState />);
    const link = screen.getByRole("link");
    expect(link.getAttribute("href")).toBe("/check");
  });
});
