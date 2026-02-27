import { render, screen, cleanup } from "@testing-library/react";
import { describe, it, expect, afterEach, vi } from "vitest";
import { Header } from "./Header";

afterEach(cleanup);

vi.mock("next/navigation", () => ({
  usePathname: () => "/",
}));

describe("Header", () => {
  it("renders the brand name", () => {
    render(<Header />);
    expect(screen.getAllByText("PillRight").length).toBeGreaterThanOrEqual(1);
  });

  it("renders navigation links", () => {
    render(<Header />);
    expect(screen.getAllByText("상호작용 체크").length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText("건강팁").length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText("내 복약함").length).toBeGreaterThanOrEqual(1);
  });
});
