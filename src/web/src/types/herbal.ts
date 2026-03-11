/** 한약재(생약) 관련 타입 정의 — 백엔드 스키마 1:1 매칭. */

export interface HerbalMedicineSearchItem {
  id: number;
  name: string;
  slug: string;
  korean_name: string | null;
  category: string | null;
  image_url: string | null;
}

export interface HerbalMedicineDetail {
  id: number;
  name: string;
  slug: string;
  korean_name: string | null;
  latin_name: string | null;
  category: string | null;
  properties: Record<string, unknown> | null;
  description: string | null;
  efficacy: string | null;
  precautions: string | null;
  image_url: string | null;
}
