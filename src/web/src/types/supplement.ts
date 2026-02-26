/** 영양제(건강기능식품) 관련 타입 정의 — 백엔드 스키마 1:1 매칭. */

export interface SupplementSearchItem {
  id: number;
  product_name: string;
  slug: string;
  company: string | null;
  main_ingredient: string | null;
  category: string | null;
}

export interface SupplementDetail {
  id: number;
  product_name: string;
  slug: string;
  company: string | null;
  registration_no: string | null;
  main_ingredient: string | null;
  ingredients: Record<string, unknown>[] | null;
  functionality: string | null;
  precautions: string | null;
  intake_method: string | null;
  category: string | null;
  source: string | null;
}
