/** 영양제 API. */

import { fetchApi } from "./client";
import type { SupplementSearchItem, SupplementDetail } from "@/types/supplement";
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

/** slug로 영양제 상세 조회 (SSG용). */
export function getSupplementBySlug(slug: string): Promise<SupplementDetail> {
  return fetchApi<SupplementDetail>(`/api/v1/supplements/by-slug/${slug}`);
}

/** 전체 영양제 slug 목록 (generateStaticParams용). */
export function getAllSupplementSlugs(): Promise<string[]> {
  return fetchApi<string[]>("/api/v1/supplements/slugs");
}

/** 관련 영양제 검색 (같은 카테고리 기반, 상세 페이지용). */
export async function getRelatedSupplements(
  category: string | null,
  excludeSlug: string,
  limit = 5,
): Promise<SupplementSearchItem[]> {
  if (!category) return [];
  try {
    const res = await searchSupplements(category, 1, limit + 1);
    return res.items
      .filter((s) => s.slug !== excludeSlug)
      .slice(0, limit);
  } catch {
    return [];
  }
}
