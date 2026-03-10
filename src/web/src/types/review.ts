/** 리뷰 관련 타입 정의 — 백엔드 스키마 1:1 매칭. */

export interface ReviewCreate {
  rating: number;
  effectiveness?: number | null;
  ease_of_use?: number | null;
  comment?: string | null;
  recaptcha_token?: string | null;
}

export interface ReviewResponse {
  id: number;
  device_id: string;
  item_type: string;
  item_id: number;
  rating: number;
  effectiveness: number | null;
  ease_of_use: number | null;
  comment: string | null;
  helpful_count: number;
  created_at: string;
  updated_at: string;
}

export interface ReviewSummary {
  average_rating: number;
  total_count: number;
  distribution: Record<string, number>;
}

export interface ReviewListResponse {
  items: ReviewResponse[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}
