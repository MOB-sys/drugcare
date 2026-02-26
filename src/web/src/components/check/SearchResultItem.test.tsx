import { render, screen, cleanup, fireEvent } from "@testing-library/react";
import { describe, it, expect, afterEach, vi } from "vitest";
import { SearchResultItem } from "./SearchResultItem";

afterEach(cleanup);

describe("SearchResultItem", () => {
  it("renders drug item with badge", () => {
    render(
      <SearchResultItem
        name="타이레놀"
        sub="한국얀센"
        itemType="drug"
        selected={false}
        disabled={false}
        onToggle={vi.fn()}
      />,
    );
    expect(screen.getAllByText("타이레놀").length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText("약물").length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText("한국얀센").length).toBeGreaterThanOrEqual(1);
  });

  it("renders supplement item with badge", () => {
    render(
      <SearchResultItem
        name="오메가3"
        sub={null}
        itemType="supplement"
        selected={false}
        disabled={false}
        onToggle={vi.fn()}
      />,
    );
    expect(screen.getAllByText("영양제").length).toBeGreaterThanOrEqual(1);
  });

  it("calls onToggle when clicked", () => {
    const onToggle = vi.fn();
    render(
      <SearchResultItem
        name="타이레놀"
        sub={null}
        itemType="drug"
        selected={false}
        disabled={false}
        onToggle={onToggle}
      />,
    );
    fireEvent.click(screen.getByText("타이레놀"));
    expect(onToggle).toHaveBeenCalled();
  });
});
