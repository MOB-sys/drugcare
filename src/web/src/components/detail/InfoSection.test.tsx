import { render, screen, cleanup } from "@testing-library/react";
import { describe, it, expect, afterEach } from "vitest";
import { InfoSection } from "./InfoSection";

afterEach(cleanup);

describe("InfoSection", () => {
  it("renders title and content", () => {
    render(<InfoSection title="효능·효과" content="해열 및 진통 효과" />);
    expect(screen.getAllByText("효능·효과").length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText("해열 및 진통 효과").length).toBeGreaterThanOrEqual(1);
  });

  it("renders nothing when content is null", () => {
    const { container } = render(<InfoSection title="효능·효과" content={null} />);
    expect(container.innerHTML).toBe("");
  });

  it("preserves newlines with whitespace-pre-line", () => {
    render(<InfoSection title="용법" content={"1일 3회\n1회 1정"} />);
    const el = screen.getByText(/1일 3회/);
    expect(el.className).toContain("whitespace-pre-line");
  });
});
