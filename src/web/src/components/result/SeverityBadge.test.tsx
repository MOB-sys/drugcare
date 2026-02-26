import { render, screen, cleanup } from "@testing-library/react";
import { describe, it, expect, afterEach } from "vitest";
import { SeverityBadge } from "./SeverityBadge";

afterEach(cleanup);

describe("SeverityBadge", () => {
  it("renders danger label", () => {
    render(<SeverityBadge severity="danger" />);
    expect(screen.getAllByText("위험").length).toBeGreaterThanOrEqual(1);
  });

  it("renders warning label", () => {
    render(<SeverityBadge severity="warning" />);
    expect(screen.getAllByText("경고").length).toBeGreaterThanOrEqual(1);
  });

  it("renders caution label", () => {
    render(<SeverityBadge severity="caution" />);
    expect(screen.getAllByText("주의").length).toBeGreaterThanOrEqual(1);
  });

  it("renders info label", () => {
    render(<SeverityBadge severity="info" />);
    expect(screen.getAllByText("참고").length).toBeGreaterThanOrEqual(1);
  });
});
