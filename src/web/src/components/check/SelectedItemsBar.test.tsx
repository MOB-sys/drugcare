import { render, screen, cleanup, fireEvent } from "@testing-library/react";
import { describe, it, expect, afterEach, vi } from "vitest";
import { SelectedItemsBar } from "./SelectedItemsBar";

afterEach(cleanup);

describe("SelectedItemsBar", () => {
  it("renders nothing when no items", () => {
    const { container } = render(
      <SelectedItemsBar items={[]} onRemove={vi.fn()} onClearAll={vi.fn()} />,
    );
    expect(container.innerHTML).toBe("");
  });

  it("renders selected items with count", () => {
    render(
      <SelectedItemsBar
        items={[
          { item_type: "drug", item_id: 1, name: "타이레놀" },
          { item_type: "supplement", item_id: 2, name: "오메가3" },
        ]}
        onRemove={vi.fn()}
        onClearAll={vi.fn()}
      />,
    );
    expect(screen.getAllByText(/2개/).length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText("타이레놀").length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText("오메가3").length).toBeGreaterThanOrEqual(1);
  });

  it("calls onClearAll when clear button clicked", () => {
    const onClearAll = vi.fn();
    render(
      <SelectedItemsBar
        items={[{ item_type: "drug", item_id: 1, name: "타이레놀" }]}
        onRemove={vi.fn()}
        onClearAll={onClearAll}
      />,
    );
    fireEvent.click(screen.getByText("전체 해제"));
    expect(onClearAll).toHaveBeenCalled();
  });

  it("calls onRemove with correct args", () => {
    const onRemove = vi.fn();
    render(
      <SelectedItemsBar
        items={[{ item_type: "drug", item_id: 1, name: "타이레놀" }]}
        onRemove={onRemove}
        onClearAll={vi.fn()}
      />,
    );
    fireEvent.click(screen.getByLabelText("타이레놀 제거"));
    expect(onRemove).toHaveBeenCalledWith(1, "drug");
  });
});
