/** 약물 API. */

import { fetchApi } from "./client";
import type {
  DrugSearchItem,
  DrugDetail,
  DrugSideEffectItem,
  DrugIdentifyItem,
  DrugConditionItem,
} from "@/types/drug";
import type { PaginatedResponse } from "@/types/search";

export function searchDrugs(
  query: string,
  page = 1,
  pageSize = 20,
  options?: RequestInit,
): Promise<PaginatedResponse<DrugSearchItem>> {
  const params = new URLSearchParams({
    q: query,
    page: String(page),
    page_size: String(pageSize),
  });
  return fetchApi<PaginatedResponse<DrugSearchItem>>(
    `/api/v1/drugs/search?${params}`,
    options,
  );
}

/** slug로 약물 상세 조회 (SSG용). */
export function getDrugBySlug(slug: string): Promise<DrugDetail> {
  if (!/^[a-z0-9가-힣ㄱ-ㅎㅏ-ㅣ\-]+$/i.test(slug)) {
    throw new Error("Invalid slug format");
  }
  return fetchApi<DrugDetail>(`/api/v1/drugs/by-slug/${slug}`);
}

/** 전체 약물 slug 목록 (generateStaticParams용). */
export function getAllDrugSlugs(): Promise<string[]> {
  return fetchApi<string[]>("/api/v1/drugs/slugs");
}

/** 초성/알파벳별 약물 조회 (페이지네이션). */
export function browseDrugsByLetter(
  letter: string,
  page = 1,
  pageSize = 50,
): Promise<PaginatedResponse<DrugSearchItem>> {
  const params = new URLSearchParams({
    letter,
    page: String(page),
    page_size: String(pageSize),
  });
  return fetchApi<PaginatedResponse<DrugSearchItem>>(
    `/api/v1/drugs/browse?${params}`,
  );
}

/** 초성/알파벳별 약물 건수 조회. */
export function getDrugBrowseCounts(): Promise<Record<string, number>> {
  return fetchApi<Record<string, number>>("/api/v1/drugs/browse/counts");
}

/** 부작용 키워드로 약물 검색. */
export function searchDrugsBySideEffect(
  q: string,
  page = 1,
  pageSize = 20,
): Promise<PaginatedResponse<DrugSideEffectItem>> {
  const params = new URLSearchParams({
    q,
    page: String(page),
    page_size: String(pageSize),
  });
  return fetchApi<PaginatedResponse<DrugSideEffectItem>>(
    `/api/v1/drugs/side-effects/search?${params}`,
  );
}

/** 약 식별 (색상/모양/각인). */
export function identifyDrug(
  color?: string | null,
  shape?: string | null,
  imprint?: string | null,
  page = 1,
  pageSize = 20,
): Promise<PaginatedResponse<DrugIdentifyItem>> {
  const params = new URLSearchParams({
    page: String(page),
    page_size: String(pageSize),
  });
  if (color) params.set("color", color);
  if (shape) params.set("shape", shape);
  if (imprint) params.set("imprint", imprint);
  return fetchApi<PaginatedResponse<DrugIdentifyItem>>(
    `/api/v1/drugs/identify?${params}`,
  );
}

/** 질환별 약물 주의사항 검색. */
export function searchDrugsByCondition(
  q: string,
  page = 1,
  pageSize = 20,
): Promise<PaginatedResponse<DrugConditionItem>> {
  const params = new URLSearchParams({
    q,
    page: String(page),
    page_size: String(pageSize),
  });
  return fetchApi<PaginatedResponse<DrugConditionItem>>(
    `/api/v1/drugs/conditions/search?${params}`,
  );
}

/** 증상 키워드로 약물 검색. */
export function searchDrugsBySymptom(
  q: string,
  page = 1,
  pageSize = 20,
): Promise<PaginatedResponse<DrugSearchItem>> {
  const params = new URLSearchParams({
    q,
    page: String(page),
    page_size: String(pageSize),
  });
  return fetchApi<PaginatedResponse<DrugSearchItem>>(
    `/api/v1/drugs/symptoms/search?${params}`,
  );
}

/** 최근 등록 의약품 목록. */
export function getRecentDrugs(
  days = 30,
  limit = 20,
): Promise<DrugSearchItem[]> {
  const params = new URLSearchParams({
    days: String(days),
    limit: String(limit),
  });
  return fetchApi<DrugSearchItem[]>(`/api/v1/drugs/recent?${params}`);
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
  } catch (error) {
    console.error("[getRelatedDrugs] Failed to fetch related drugs:", error);
    return [];
  }
}
