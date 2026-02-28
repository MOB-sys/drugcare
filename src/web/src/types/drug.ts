/** 의약품 관련 타입 정의 — 백엔드 스키마 1:1 매칭. */

export interface IngredientInfo {
  name: string;
  amount: string | null;
  unit: string | null;
}

export interface DrugSearchItem {
  id: number;
  item_seq: string;
  item_name: string;
  slug: string;
  entp_name: string | null;
  etc_otc_code: string | null;
  class_no: string | null;
  item_image: string | null;
}

export interface DURSafetyItem {
  dur_type: string;
  type_name: string | null;
  ingr_name: string | null;
  prohibition_content: string | null;
  remark: string | null;
}

export interface DrugDetail {
  id: number;
  item_seq: string;
  item_name: string;
  slug: string;
  entp_name: string | null;
  etc_otc_code: string | null;
  class_no: string | null;
  chart: string | null;
  bar_code: string | null;
  material_name: string | null;
  ingredients: IngredientInfo[] | null;
  efcy_qesitm: string | null;
  use_method_qesitm: string | null;
  atpn_warn_qesitm: string | null;
  atpn_qesitm: string | null;
  intrc_qesitm: string | null;
  se_qesitm: string | null;
  deposit_method_qesitm: string | null;
  item_image: string | null;
  dur_safety: DURSafetyItem[] | null;
}
