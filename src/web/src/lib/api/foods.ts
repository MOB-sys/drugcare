/** 식품 API. */

import { fetchApi } from "./client";
import type { FoodSearchItem, FoodDetail } from "@/types/food";
import type { PaginatedResponse } from "@/types/search";

export function searchFoods(
  query: string,
  page = 1,
  pageSize = 20,
  options?: RequestInit,
): Promise<PaginatedResponse<FoodSearchItem>> {
  const params = new URLSearchParams({
    q: query,
    page: String(page),
    page_size: String(pageSize),
  });
  return fetchApi<PaginatedResponse<FoodSearchItem>>(
    `/api/v1/foods/search?${params}`,
    options,
  );
}

/** slug로 식품 상세 조회 (SSG용). */
export function getFoodBySlug(slug: string): Promise<FoodDetail> {
  if (!/^[a-z0-9가-힣ㄱ-ㅎㅏ-ㅣ\-]+$/i.test(slug)) {
    throw new Error("Invalid slug format");
  }
  return fetchApi<FoodDetail>(`/api/v1/foods/by-slug/${slug}`);
}

/** 전체 식품 slug 목록 (generateStaticParams용). */
export function getAllFoodSlugs(): Promise<string[]> {
  return fetchApi<string[]>("/api/v1/foods/slugs");
}

/** 전체 식품 목록 조회 (빈 쿼리로 전체 반환). */
export function getAllFoods(
  page = 1,
  pageSize = 100,
): Promise<PaginatedResponse<FoodSearchItem>> {
  const params = new URLSearchParams({
    q: "",
    page: String(page),
    page_size: String(pageSize),
  });
  return fetchApi<PaginatedResponse<FoodSearchItem>>(
    `/api/v1/foods/search?${params}`,
  );
}

/** 식품 총 건수 조회. */
export function getFoodCount(): Promise<number> {
  return fetchApi<number>("/api/v1/foods/count");
}
