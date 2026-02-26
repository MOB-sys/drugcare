/** 상호작용 체크 관련 타입 정의 — 백엔드 스키마 1:1 매칭. */

export interface InteractionCheckItem {
  item_type: "drug" | "supplement";
  item_id: number;
}

export interface InteractionResult {
  item_a_name: string;
  item_b_name: string;
  severity: "danger" | "warning" | "caution" | "info";
  description: string | null;
  mechanism: string | null;
  recommendation: string | null;
  source: string;
  evidence_level: string | null;
  ai_explanation: string | null;
  ai_recommendation: string | null;
}

export interface InteractionCheckResponse {
  total_checked: number;
  interactions_found: number;
  has_danger: boolean;
  results: InteractionResult[];
  disclaimer: string;
}
