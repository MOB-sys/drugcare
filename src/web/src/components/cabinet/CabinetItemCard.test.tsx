import { render, screen, cleanup, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi, afterEach } from "vitest";
import { CabinetItemCard } from "./CabinetItemCard";
import type { CabinetItem } from "@/types/cabinet";

afterEach(cleanup);

const ITEM: CabinetItem = {
  id: 1,
  device_id: "test",
  item_type: "drug",
  item_id: 10,
  item_name: "타이레놀",
  nickname: "타이레놀",
  created_at: "2026-01-15T00:00:00Z",
};

describe("CabinetItemCard", () => {
  it("renders item name and type badge", () => {
    render(<CabinetItemCard item={ITEM} onDelete={() => {}} />);
    expect(screen.getAllByText("타이레놀").length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText("의약품").length).toBeGreaterThanOrEqual(1);
  });

  it("renders supplement badge", () => {
    const suppItem = { ...ITEM, item_type: "supplement" as const };
    render(<CabinetItemCard item={suppItem} onDelete={() => {}} />);
    expect(screen.getAllByText("영양제").length).toBeGreaterThanOrEqual(1);
  });

  it("calls onDelete when delete button clicked", () => {
    const onDelete = vi.fn();
    render(<CabinetItemCard item={ITEM} onDelete={onDelete} />);
    fireEvent.click(screen.getByRole("button", { name: /삭제/ }));
    expect(onDelete).toHaveBeenCalledWith(1);
  });
});
