import { render, screen, cleanup, fireEvent, waitFor } from "@testing-library/react";
import { describe, it, expect, vi, afterEach, beforeEach } from "vitest";
import { AddToCabinetButton } from "./AddToCabinetButton";
import { ToastProvider } from "@/components/common/ToastProvider";

function renderWithToast(ui: React.ReactElement) {
  return render(<ToastProvider>{ui}</ToastProvider>);
}

afterEach(cleanup);

function mockFetchOk() {
  global.fetch = vi.fn().mockResolvedValue({
    ok: true,
    status: 200,
    json: () =>
      Promise.resolve({
        success: true,
        data: { id: 1, item_type: "drug", item_id: 10, item_name: "타이레놀", nickname: "타이레놀", created_at: "" },
        error: null,
        meta: { timestamp: "" },
      }),
  });
}

function mockFetch409() {
  global.fetch = vi.fn().mockResolvedValue({
    ok: false,
    status: 409,
    json: () =>
      Promise.resolve({ success: false, data: null, error: "이미 존재", meta: { timestamp: "" } }),
  });
}

beforeEach(() => {
  mockFetchOk();
});

afterEach(() => {
  vi.restoreAllMocks();
});

describe("AddToCabinetButton", () => {
  it("renders default label", () => {
    renderWithToast(<AddToCabinetButton itemType="drug" itemId={10} itemName="타이레놀" />);
    expect(screen.getAllByText("복약함에 추가").length).toBeGreaterThanOrEqual(1);
  });

  it("shows added state on success", async () => {
    renderWithToast(<AddToCabinetButton itemType="drug" itemId={10} itemName="타이레놀" />);
    fireEvent.click(screen.getByRole("button"));
    await waitFor(() => {
      expect(screen.getAllByText("추가됨!").length).toBeGreaterThanOrEqual(1);
    });
  });

  it("shows duplicate state on 409", async () => {
    mockFetch409();
    renderWithToast(<AddToCabinetButton itemType="drug" itemId={10} itemName="타이레놀" />);
    fireEvent.click(screen.getByRole("button"));
    await waitFor(() => {
      expect(screen.getAllByText("이미 추가됨").length).toBeGreaterThanOrEqual(1);
    });
  });
});
