/** 리뷰 API. */

import { fetchApi } from "./client";
import type {
  ReviewCreate,
  ReviewResponse,
  ReviewSummary,
  ReviewListResponse,
} from "@/types/review";

function validateItemType(itemType: string): asserts itemType is "drug" | "supplement" {
  if (itemType !== "drug" && itemType !== "supplement") {
    throw new Error(`Invalid item type: ${itemType}`);
  }
}

/** 리뷰 작성/수정 (upsert). */
export function createReview(
  itemType: string,
  itemId: number,
  data: ReviewCreate,
): Promise<ReviewResponse> {
  validateItemType(itemType);
  const params = new URLSearchParams({
    item_type: itemType,
    item_id: String(itemId),
  });
  return fetchApi<ReviewResponse>(`/api/v1/reviews/?${params}`, {
    method: "POST",
    body: JSON.stringify(data),
  });
}

/** 리뷰 목록 조회 (페이지네이션). */
export function getReviews(
  itemType: string,
  itemId: number,
  page = 1,
  pageSize = 10,
): Promise<ReviewListResponse> {
  validateItemType(itemType);
  const params = new URLSearchParams({
    page: String(page),
    page_size: String(pageSize),
  });
  return fetchApi<ReviewListResponse>(
    `/api/v1/reviews/${itemType}/${itemId}?${params}`,
  );
}

/** 리뷰 요약 통계 조회. */
export function getReviewSummary(
  itemType: string,
  itemId: number,
): Promise<ReviewSummary> {
  validateItemType(itemType);
  return fetchApi<ReviewSummary>(
    `/api/v1/reviews/${itemType}/${itemId}/summary`,
  );
}

/** 도움됨 표시. */
export function markHelpful(reviewId: number): Promise<ReviewResponse> {
  return fetchApi<ReviewResponse>(`/api/v1/reviews/${reviewId}/helpful`, {
    method: "POST",
  });
}

/** 리뷰 삭제. */
export function deleteReview(reviewId: number): Promise<boolean> {
  return fetchApi<boolean>(`/api/v1/reviews/${reviewId}`, {
    method: "DELETE",
  });
}
