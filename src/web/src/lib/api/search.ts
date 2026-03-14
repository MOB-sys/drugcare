/** 통합 검색 API — 자동완성 제안. */

import { fetchApi } from "./client";

export interface SearchSuggestion {
  name: string;
  slug: string;
  type: "drug" | "supplement" | "food" | "herbal";
}

/** 전체 타입 통합 자동완성 제안을 가져온다. */
export async function fetchSearchSuggestions(
  q: string,
  limit = 10,
): Promise<SearchSuggestion[]> {
  if (!q || q.length < 2) return [];
  const data = await fetchApi<SearchSuggestion[]>(
    `/api/v1/search/suggest?q=${encodeURIComponent(q)}&limit=${limit}`,
  );
  return data ?? [];
}
