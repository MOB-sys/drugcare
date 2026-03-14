import { describe, it, expect, vi, beforeEach } from "vitest";
import { fetchSearchSuggestions } from "./search";

// fetchApi를 모킹
vi.mock("./client", () => ({
  fetchApi: vi.fn(),
}));

import { fetchApi } from "./client";
const mockFetchApi = vi.mocked(fetchApi);

beforeEach(() => {
  vi.clearAllMocks();
});

describe("fetchSearchSuggestions", () => {
  it("returns empty array for short query", async () => {
    const result = await fetchSearchSuggestions("타");
    expect(result).toEqual([]);
    expect(mockFetchApi).not.toHaveBeenCalled();
  });

  it("returns empty array for empty query", async () => {
    const result = await fetchSearchSuggestions("");
    expect(result).toEqual([]);
    expect(mockFetchApi).not.toHaveBeenCalled();
  });

  it("fetches suggestions for valid query", async () => {
    const mockData = [
      { name: "타이레놀", slug: "drug-1", type: "drug" as const },
      { name: "타우린", slug: "supp-1", type: "supplement" as const },
    ];
    mockFetchApi.mockResolvedValue(mockData);

    const result = await fetchSearchSuggestions("타이레", 8);

    expect(result).toEqual(mockData);
    expect(mockFetchApi).toHaveBeenCalledWith(
      `/api/v1/search/suggest?q=${encodeURIComponent("타이레")}&limit=8`,
    );
  });

  it("returns empty array when API returns null", async () => {
    mockFetchApi.mockResolvedValue(null);

    const result = await fetchSearchSuggestions("비타민");

    expect(result).toEqual([]);
  });

  it("uses default limit of 10", async () => {
    mockFetchApi.mockResolvedValue([]);

    await fetchSearchSuggestions("비타민");

    expect(mockFetchApi).toHaveBeenCalledWith(
      expect.stringContaining("&limit=10"),
    );
  });
});
