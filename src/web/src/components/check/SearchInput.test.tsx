import { render, screen, cleanup, fireEvent } from "@testing-library/react";
import { describe, it, expect, afterEach, vi } from "vitest";
import { SearchInput } from "./SearchInput";

afterEach(cleanup);

describe("SearchInput", () => {
  it("renders placeholder text", () => {
    render(<SearchInput value="" onChange={vi.fn()} />);
    expect(
      screen.getAllByPlaceholderText("약물 또는 영양제를 검색하세요").length,
    ).toBeGreaterThanOrEqual(1);
  });

  it("calls onChange when typing", () => {
    const onChange = vi.fn();
    render(<SearchInput value="" onChange={onChange} />);
    const input = screen.getByPlaceholderText("약물 또는 영양제를 검색하세요");
    fireEvent.change(input, { target: { value: "타이레놀" } });
    expect(onChange).toHaveBeenCalledWith("타이레놀");
  });

  it("shows clear button when value exists", () => {
    render(<SearchInput value="타이레놀" onChange={vi.fn()} />);
    expect(
      screen.getAllByLabelText("검색어 지우기").length,
    ).toBeGreaterThanOrEqual(1);
  });

  it("clears input when clear button clicked", () => {
    const onChange = vi.fn();
    render(<SearchInput value="타이레놀" onChange={onChange} />);
    fireEvent.click(screen.getByLabelText("검색어 지우기"));
    expect(onChange).toHaveBeenCalledWith("");
  });
});
