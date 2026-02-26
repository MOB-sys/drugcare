import { render, screen, cleanup, fireEvent } from "@testing-library/react";
import { describe, it, expect, afterEach, vi } from "vitest";
import { FilterChips } from "./FilterChips";

afterEach(cleanup);

describe("FilterChips", () => {
  it("renders all filter options", () => {
    render(<FilterChips current="all" onChange={vi.fn()} />);
    expect(screen.getAllByText("전체").length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText("약물").length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText("영양제").length).toBeGreaterThanOrEqual(1);
  });

  it("calls onChange with correct filter", () => {
    const onChange = vi.fn();
    render(<FilterChips current="all" onChange={onChange} />);
    fireEvent.click(screen.getByText("약물"));
    expect(onChange).toHaveBeenCalledWith("drug");
  });
});
