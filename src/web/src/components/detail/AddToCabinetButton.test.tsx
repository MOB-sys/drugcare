import { render, screen, cleanup, fireEvent, waitFor } from "@testing-library/react";
import { describe, it, expect, vi, afterEach, beforeEach } from "vitest";
import { AddToCabinetButton } from "./AddToCabinetButton";
import { ToastProvider } from "@/components/common/ToastProvider";

vi.mock("@/lib/api/cabinet", () => ({
  addCabinetItem: vi.fn(),
  deleteCabinetItem: vi.fn(),
}));

import { addCabinetItem } from "@/lib/api/cabinet";

function renderWithToast(ui: React.ReactElement) {
  return render(<ToastProvider>{ui}</ToastProvider>);
}

afterEach(cleanup);

afterEach(() => {
  vi.restoreAllMocks();
});

describe("AddToCabinetButton", () => {
  it("renders default label", () => {
    renderWithToast(<AddToCabinetButton itemType="drug" itemId={10} itemName="타이레놀" />);
    expect(screen.getAllByText("복약함에 추가").length).toBeGreaterThanOrEqual(1);
  });

  it("shows added state on success", async () => {
    vi.mocked(addCabinetItem).mockResolvedValue({
      id: 1,
      device_id: "test",
      item_type: "drug",
      item_id: 10,
      item_name: "타이레놀",
      nickname: "타이레놀",
      created_at: "",
    });
    renderWithToast(<AddToCabinetButton itemType="drug" itemId={10} itemName="타이레놀" />);
    fireEvent.click(screen.getByRole("button"));
    await waitFor(() => {
      expect(screen.getAllByText("추가됨").length).toBeGreaterThanOrEqual(1);
    });
  });

  it("shows duplicate state on 409", async () => {
    const { ApiError } = await import("@/lib/api/client");
    vi.mocked(addCabinetItem).mockRejectedValue(new ApiError(409, "이미 존재"));
    renderWithToast(<AddToCabinetButton itemType="drug" itemId={10} itemName="타이레놀" />);
    fireEvent.click(screen.getByRole("button"));
    await waitFor(() => {
      expect(screen.getAllByText("이미 추가됨").length).toBeGreaterThanOrEqual(1);
    });
  });
});
