/** 식품 관련 타입 정의 — 백엔드 스키마 1:1 매칭. */

export interface FoodSearchItem {
  id: number;
  name: string;
  slug: string;
  category: string | null;
  image_url: string | null;
}

export interface FoodDetail {
  id: number;
  name: string;
  slug: string;
  category: string | null;
  description: string | null;
  common_names: string[] | null;
  nutrients: Record<string, unknown>[] | null;
  image_url: string | null;
}
