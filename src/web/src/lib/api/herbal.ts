/** 한약재 API. */

import { fetchApi } from "./client";
import type { HerbalMedicineSearchItem, HerbalMedicineDetail } from "@/types/herbal";
import type { PaginatedResponse } from "@/types/search";

export function searchHerbalMedicines(
  query: string,
  page = 1,
  pageSize = 20,
  options?: RequestInit,
): Promise<PaginatedResponse<HerbalMedicineSearchItem>> {
  const params = new URLSearchParams({
    q: query,
    page: String(page),
    page_size: String(pageSize),
  });
  return fetchApi<PaginatedResponse<HerbalMedicineSearchItem>>(
    `/api/v1/herbal-medicines/search?${params}`,
    options,
  );
}

/** slug로 한약재 상세 조회 (SSG용). */
export function getHerbalMedicineBySlug(slug: string): Promise<HerbalMedicineDetail> {
  if (!/^[a-z0-9가-힣ㄱ-ㅎㅏ-ㅣ\-]+$/i.test(slug)) {
    throw new Error("Invalid slug format");
  }
  return fetchApi<HerbalMedicineDetail>(`/api/v1/herbal-medicines/by-slug/${slug}`);
}

/** 전체 한약재 slug 목록 (generateStaticParams용). */
export function getAllHerbalMedicineSlugs(): Promise<string[]> {
  return fetchApi<string[]>("/api/v1/herbal-medicines/slugs");
}

/** 전체 한약재 목록 조회 (빈 쿼리로 전체 반환). */
export function getAllHerbalMedicines(
  page = 1,
  pageSize = 100,
): Promise<PaginatedResponse<HerbalMedicineSearchItem>> {
  const params = new URLSearchParams({
    q: "",
    page: String(page),
    page_size: String(pageSize),
  });
  return fetchApi<PaginatedResponse<HerbalMedicineSearchItem>>(
    `/api/v1/herbal-medicines/search?${params}`,
  );
}

/** 한약재 총 건수 조회. */
export function getHerbalMedicineCount(): Promise<number> {
  return fetchApi<number>("/api/v1/herbal-medicines/count");
}
