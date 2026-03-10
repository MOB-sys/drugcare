/** 질환별 약물 주의사항 — 주요 질환/대상 목록. */

export interface ConditionItem {
  keyword: string;
  label: string;
  description: string;
}

export const CONDITIONS: ConditionItem[] = [
  { keyword: "간질환", label: "간질환", description: "간염, 간경변, 지방간 등 간 기능 이상" },
  { keyword: "신장질환", label: "신장질환", description: "신부전, 신증후군 등 신장 기능 이상" },
  { keyword: "당뇨", label: "당뇨", description: "제1형/제2형 당뇨병" },
  { keyword: "고혈압", label: "고혈압", description: "혈압이 정상 범위를 초과하는 상태" },
  { keyword: "심장질환", label: "심장질환", description: "심부전, 부정맥, 협심증 등" },
  { keyword: "천식", label: "천식", description: "기관지 과민성으로 인한 호흡기 질환" },
  { keyword: "위궤양", label: "위궤양", description: "위장관 점막의 궤양성 질환" },
  { keyword: "임부", label: "임부", description: "임신 중인 여성에 대한 주의사항" },
  { keyword: "수유부", label: "수유부", description: "모유 수유 중인 여성에 대한 주의사항" },
  { keyword: "소아", label: "소아", description: "15세 미만 어린이에 대한 주의사항" },
  { keyword: "고령자", label: "고령자", description: "65세 이상 고령자에 대한 주의사항" },
  { keyword: "녹내장", label: "녹내장", description: "안압 상승으로 인한 시신경 손상" },
  { keyword: "전립선비대", label: "전립선비대", description: "배뇨 장애를 동반하는 전립선 비대" },
  { keyword: "갑상선", label: "갑상선", description: "갑상선기능항진/저하증" },
  { keyword: "알레르기", label: "알레르기", description: "약물 과민반응, 아나필락시스 등" },
  { keyword: "뇌전증", label: "뇌전증", description: "반복적 발작을 동반하는 신경 질환" },
  { keyword: "우울증", label: "우울증", description: "기분장애, 항우울제 관련 주의사항" },
  { keyword: "혈액응고", label: "혈액응고", description: "출혈 경향, 항응고제 복용 관련" },
  { keyword: "골다공증", label: "골다공증", description: "뼈 밀도 감소 관련 주의사항" },
  { keyword: "결핵", label: "결핵", description: "결핵 치료제 관련 주의사항" },
];
