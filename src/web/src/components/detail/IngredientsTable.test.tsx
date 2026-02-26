import { render, screen, cleanup } from "@testing-library/react";
import { describe, it, expect, afterEach } from "vitest";
import { IngredientsTable } from "./IngredientsTable";
import type { IngredientInfo } from "@/types/drug";

afterEach(cleanup);

const INGREDIENTS: IngredientInfo[] = [
  { name: "아세트아미노펜", amount: "500", unit: "mg" },
  { name: "카페인", amount: "50", unit: "mg" },
];

describe("IngredientsTable", () => {
  it("renders table headers", () => {
    render(<IngredientsTable ingredients={INGREDIENTS} />);
    expect(screen.getAllByText("성분명").length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText("함량").length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText("단위").length).toBeGreaterThanOrEqual(1);
  });

  it("renders ingredient rows", () => {
    render(<IngredientsTable ingredients={INGREDIENTS} />);
    expect(screen.getAllByText("아세트아미노펜").length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText("500").length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText("카페인").length).toBeGreaterThanOrEqual(1);
  });

  it("shows dash for null amount/unit", () => {
    render(<IngredientsTable ingredients={[{ name: "비타민C", amount: null, unit: null }]} />);
    expect(screen.getAllByText("-").length).toBeGreaterThanOrEqual(2);
  });

  it("renders nothing for empty array", () => {
    const { container } = render(<IngredientsTable ingredients={[]} />);
    expect(container.innerHTML).toBe("");
  });
});
