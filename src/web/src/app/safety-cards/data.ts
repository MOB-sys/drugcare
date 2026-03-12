/** SNS 콘텐츠 인덱스 — web_exporter가 생성한 index.json을 타입 안전하게 import. */

import indexJson from "../../../public/sns-content/index.json";

export interface SafetyCardItem {
  id: string;
  title: string;
  severity: string;
  danger_score: number;
  thumb: string;
}

export interface SafetyCardIndex {
  total: number;
  exported_at: string;
  items: SafetyCardItem[];
}

const indexData: SafetyCardIndex = indexJson;
export default indexData;
