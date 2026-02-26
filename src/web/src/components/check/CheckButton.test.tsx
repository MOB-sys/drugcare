import { render, screen, cleanup, fireEvent } from "@testing-library/react";
import { describe, it, expect, afterEach, vi } from "vitest";
import { CheckButton } from "./CheckButton";

afterEach(cleanup);

describe("CheckButton", () => {
  it("shows disabled state when less than 2 items", () => {
    render(
      <CheckButton
        items={[{ item_type: "drug", item_id: 1, name: "타이레놀" }]}
        isLoading={false}
        onClick={vi.fn()}
      />,
    );
    expect(screen.getAllByText(/2개 이상 선택하세요/).length).toBeGreaterThanOrEqual(1);
  });

  it("shows count when enough items selected", () => {
    render(
      <CheckButton
        items={[
          { item_type: "drug", item_id: 1, name: "타이레놀" },
          { item_type: "supplement", item_id: 2, name: "오메가3" },
        ]}
        isLoading={false}
        onClick={vi.fn()}
      />,
    );
    expect(screen.getAllByText(/상호작용 확인 \(2개\)/).length).toBeGreaterThanOrEqual(1);
  });

  it("shows loading text", () => {
    render(
      <CheckButton
        items={[
          { item_type: "drug", item_id: 1, name: "타이레놀" },
          { item_type: "supplement", item_id: 2, name: "오메가3" },
        ]}
        isLoading={true}
        onClick={vi.fn()}
      />,
    );
    expect(screen.getAllByText("확인 중...").length).toBeGreaterThanOrEqual(1);
  });

  it("calls onClick when clickable", () => {
    const onClick = vi.fn();
    render(
      <CheckButton
        items={[
          { item_type: "drug", item_id: 1, name: "타이레놀" },
          { item_type: "supplement", item_id: 2, name: "오메가3" },
        ]}
        isLoading={false}
        onClick={onClick}
      />,
    );
    fireEvent.click(screen.getByText(/상호작용 확인/));
    expect(onClick).toHaveBeenCalled();
  });
});
