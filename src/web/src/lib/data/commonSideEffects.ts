/** 자주 검색되는 부작용 키워드 목록. */

export interface SideEffectItem {
  label: string;
  keyword: string;
}

export const COMMON_SIDE_EFFECTS: SideEffectItem[] = [
  { label: "두통", keyword: "두통" },
  { label: "어지러움", keyword: "어지러움" },
  { label: "졸음", keyword: "졸음" },
  { label: "구역", keyword: "구역" },
  { label: "구토", keyword: "구토" },
  { label: "설사", keyword: "설사" },
  { label: "변비", keyword: "변비" },
  { label: "발진", keyword: "발진" },
  { label: "가려움", keyword: "가려움" },
  { label: "불면", keyword: "불면" },
  { label: "피로", keyword: "피로" },
  { label: "식욕부진", keyword: "식욕부진" },
  { label: "복통", keyword: "복통" },
  { label: "소화불량", keyword: "소화불량" },
  { label: "부종", keyword: "부종" },
  { label: "근육통", keyword: "근육통" },
  { label: "빈혈", keyword: "빈혈" },
  { label: "혈압상승", keyword: "혈압" },
  { label: "기침", keyword: "기침" },
  { label: "호흡곤란", keyword: "호흡곤란" },
  { label: "위장장애", keyword: "위장" },
  { label: "간기능이상", keyword: "간기능" },
  { label: "신장장애", keyword: "신장" },
  { label: "탈모", keyword: "탈모" },
  { label: "체중증가", keyword: "체중증가" },
  { label: "입마름", keyword: "입마름" },
  { label: "시력저하", keyword: "시력" },
  { label: "이명", keyword: "이명" },
  { label: "관절통", keyword: "관절통" },
  { label: "빈맥", keyword: "빈맥" },
];
