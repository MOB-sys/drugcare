import { render, screen, cleanup, fireEvent } from "@testing-library/react";
import { describe, it, expect, afterEach } from "vitest";
import { InteractionCard } from "./InteractionCard";
import type { InteractionResult } from "@/types/interaction";

afterEach(cleanup);

const mockInteraction: InteractionResult = {
  item_a_name: "타이레놀",
  item_b_name: "오메가3",
  severity: "warning",
  description: "병용 시 주의가 필요합니다",
  mechanism: "간 대사 경쟁",
  recommendation: "시간 간격을 두고 복용",
  source: "식약처",
  evidence_level: "높음",
  ai_explanation: "AI가 설명하는 내용입니다",
  ai_recommendation: "AI 권장 사항입니다",
};

describe("InteractionCard", () => {
  it("renders item names and severity", () => {
    render(<InteractionCard interaction={mockInteraction} />);
    expect(screen.getAllByText(/타이레놀/).length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText(/오메가3/).length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText("경고").length).toBeGreaterThanOrEqual(1);
  });

  it("renders description", () => {
    render(<InteractionCard interaction={mockInteraction} />);
    expect(
      screen.getAllByText("병용 시 주의가 필요합니다").length,
    ).toBeGreaterThanOrEqual(1);
  });

  it("expands to show details on click", () => {
    render(<InteractionCard interaction={mockInteraction} />);
    fireEvent.click(screen.getByText(/타이레놀/));
    expect(screen.getAllByText("간 대사 경쟁").length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText("시간 간격을 두고 복용").length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText("AI가 설명하는 내용입니다").length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText(/식약처/).length).toBeGreaterThanOrEqual(1);
  });
});
