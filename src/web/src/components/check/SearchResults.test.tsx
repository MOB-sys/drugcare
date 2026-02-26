import { render, screen, cleanup } from "@testing-library/react";
import { describe, it, expect, afterEach, vi } from "vitest";
import { SearchResults } from "./SearchResults";

afterEach(cleanup);

describe("SearchResults", () => {
  it("shows loading state", () => {
    render(
      <SearchResults
        results={[]}
        isLoading={true}
        query="타이레놀"
        isSelected={vi.fn()}
        canAddMore={true}
        onToggle={vi.fn()}
      />,
    );
    expect(screen.getAllByText("검색 중...").length).toBeGreaterThanOrEqual(1);
  });

  it("shows empty query message", () => {
    render(
      <SearchResults
        results={[]}
        isLoading={false}
        query=""
        isSelected={vi.fn()}
        canAddMore={true}
        onToggle={vi.fn()}
      />,
    );
    expect(
      screen.getAllByText("약물이나 영양제 이름을 검색해보세요").length,
    ).toBeGreaterThanOrEqual(1);
  });

  it("shows no results message", () => {
    render(
      <SearchResults
        results={[]}
        isLoading={false}
        query="없는약"
        isSelected={vi.fn()}
        canAddMore={true}
        onToggle={vi.fn()}
      />,
    );
    expect(
      screen.getAllByText(/검색 결과가 없습니다/).length,
    ).toBeGreaterThanOrEqual(1);
  });

  it("renders result items", () => {
    render(
      <SearchResults
        results={[
          { item_type: "drug", item_id: 1, name: "타이레놀", sub: null },
        ]}
        isLoading={false}
        query="타이레놀"
        isSelected={() => false}
        canAddMore={true}
        onToggle={vi.fn()}
      />,
    );
    expect(screen.getAllByText("타이레놀").length).toBeGreaterThanOrEqual(1);
  });
});
