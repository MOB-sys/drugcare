/** 영양제 검색 API. */

import { fetchApi } from "./client";
import type { SupplementSearchItem } from "@/types/supplement";
import type { PaginatedResponse } from "@/types/search";

export function searchSupplements(
  query: string,
  page = 1,
  pageSize = 20,
): Promise<PaginatedResponse<SupplementSearchItem>> {
  const params = new URLSearchParams({
    q: query,
    page: String(page),
    page_size: String(pageSize),
  });
  return fetchApi<PaginatedResponse<SupplementSearchItem>>(
    `/api/v1/supplements/search?${params}`,
  );
}
