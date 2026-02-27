/** 약물 API. */

import { fetchApi } from "./client";
import type { DrugSearchItem, DrugDetail } from "@/types/drug";
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

/** slug로 약물 상세 조회 (SSG용). */
export function getDrugBySlug(slug: string): Promise<DrugDetail> {
  return fetchApi<DrugDetail>(`/api/v1/drugs/by-slug/${slug}`);
}

/** 전체 약물 slug 목록 (generateStaticParams용). */
export function getAllDrugSlugs(): Promise<string[]> {
  return fetchApi<string[]>("/api/v1/drugs/slugs");
}

/** 관련 약물 검색 (같은 class_no 기반, 상세 페이지용). */
export async function getRelatedDrugs(
  classNo: string | null,
  excludeSlug: string,
  limit = 5,
): Promise<DrugSearchItem[]> {
  if (!classNo) return [];
  try {
    const res = await searchDrugs(classNo, 1, limit + 1);
    return res.items
      .filter((d) => d.slug !== excludeSlug)
      .slice(0, limit);
  } catch {
    return [];
  }
}
