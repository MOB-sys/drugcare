/** 약물 검색 API. */

import { fetchApi } from "./client";
import type { DrugSearchItem } from "@/types/drug";
import type { PaginatedResponse } from "@/types/search";

export function searchDrugs(
  query: string,
  page = 1,
  pageSize = 20,
): Promise<PaginatedResponse<DrugSearchItem>> {
  const params = new URLSearchParams({
    q: query,
    page: String(page),
    page_size: String(pageSize),
  });
  return fetchApi<PaginatedResponse<DrugSearchItem>>(
    `/api/v1/drugs/search?${params}`,
  );
}
