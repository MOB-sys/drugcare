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
    const links = screen.getAllByRole("link");
    const checkLink = links.find((l) => l.getAttribute("href") === "/check");
    expect(checkLink).toBeDefined();
  });

  it("renders app store download links", () => {
    render(<EmptyState />);
    expect(screen.getByText("App Store")).toBeDefined();
    expect(screen.getByText("Google Play")).toBeDefined();
  });
});
