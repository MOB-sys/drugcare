import { render, screen, cleanup } from "@testing-library/react";
import { describe, it, expect, afterEach } from "vitest";
import { ResultSummaryCard } from "./ResultSummaryCard";
import type { InteractionCheckResponse } from "@/types/interaction";

afterEach(cleanup);

const makeData = (overrides: Partial<InteractionCheckResponse> = {}): InteractionCheckResponse => ({
  total_checked: 3,
  interactions_found: 1,
  has_danger: false,
  results: [],
  disclaimer: "면책조항",
  ...overrides,
});

describe("ResultSummaryCard", () => {
  it("shows danger message when has_danger", () => {
    render(<ResultSummaryCard data={makeData({ has_danger: true })} />);
    expect(
      screen.getAllByText("주의가 필요한 조합입니다").length,
    ).toBeGreaterThanOrEqual(1);
  });

  it("shows interaction found message", () => {
    render(<ResultSummaryCard data={makeData({ interactions_found: 2 })} />);
    expect(
      screen.getAllByText("일부 상호작용이 발견되었습니다").length,
    ).toBeGreaterThanOrEqual(1);
  });

  it("shows safe message when no interactions", () => {
    render(<ResultSummaryCard data={makeData({ interactions_found: 0 })} />);
    expect(
      screen.getAllByText("특별한 상호작용이 없습니다").length,
    ).toBeGreaterThanOrEqual(1);
  });

  it("shows stats", () => {
    render(<ResultSummaryCard data={makeData()} />);
    expect(
      screen.getAllByText(/3개 조합 확인/).length,
    ).toBeGreaterThanOrEqual(1);
  });
});
