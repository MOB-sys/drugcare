/** 증상 카테고리 및 증상 목록 데이터. */

export interface SymptomItem {
  value: string;
  label: string;
  category: string;
  categoryLabel: string;
}

export interface SymptomCategory {
  key: string;
  label: string;
  icon: string;
  symptoms: SymptomItem[];
}

export const SYMPTOM_CATEGORIES: SymptomCategory[] = [
  {
    key: "pain",
    label: "통증",
    icon: "pain",
    symptoms: [
      { value: "두통", label: "두통", category: "pain", categoryLabel: "통증" },
      { value: "치통", label: "치통", category: "pain", categoryLabel: "통증" },
      { value: "근육통", label: "근육통", category: "pain", categoryLabel: "통증" },
      { value: "관절통", label: "관절통", category: "pain", categoryLabel: "통증" },
      { value: "생리통", label: "생리통", category: "pain", categoryLabel: "통증" },
      { value: "요통", label: "요통", category: "pain", categoryLabel: "통증" },
    ],
  },
  {
    key: "digestive",
    label: "소화기",
    icon: "digestive",
    symptoms: [
      { value: "소화불량", label: "소화불량", category: "digestive", categoryLabel: "소화기" },
      { value: "속쓰림", label: "속쓰림", category: "digestive", categoryLabel: "소화기" },
      { value: "구역", label: "구역", category: "digestive", categoryLabel: "소화기" },
      { value: "구토", label: "구토", category: "digestive", categoryLabel: "소화기" },
      { value: "설사", label: "설사", category: "digestive", categoryLabel: "소화기" },
      { value: "변비", label: "변비", category: "digestive", categoryLabel: "소화기" },
      { value: "복통", label: "복통", category: "digestive", categoryLabel: "소화기" },
    ],
  },
  {
    key: "respiratory",
    label: "호흡기",
    icon: "respiratory",
    symptoms: [
      { value: "기침", label: "기침", category: "respiratory", categoryLabel: "호흡기" },
      { value: "가래", label: "가래", category: "respiratory", categoryLabel: "호흡기" },
      { value: "코막힘", label: "코막힘", category: "respiratory", categoryLabel: "호흡기" },
      { value: "콧물", label: "콧물", category: "respiratory", categoryLabel: "호흡기" },
      { value: "인후통", label: "인후통", category: "respiratory", categoryLabel: "호흡기" },
    ],
  },
  {
    key: "skin",
    label: "피부",
    icon: "skin",
    symptoms: [
      { value: "발진", label: "발진", category: "skin", categoryLabel: "피부" },
      { value: "가려움", label: "가려움", category: "skin", categoryLabel: "피부" },
      { value: "여드름", label: "여드름", category: "skin", categoryLabel: "피부" },
      { value: "무좀", label: "무좀", category: "skin", categoryLabel: "피부" },
    ],
  },
  {
    key: "other",
    label: "기타",
    icon: "other",
    symptoms: [
      { value: "발열", label: "발열", category: "other", categoryLabel: "기타" },
      { value: "알레르기", label: "알레르기", category: "other", categoryLabel: "기타" },
      { value: "불면", label: "불면", category: "other", categoryLabel: "기타" },
      { value: "피로", label: "피로", category: "other", categoryLabel: "기타" },
      { value: "빈혈", label: "빈혈", category: "other", categoryLabel: "기타" },
    ],
  },
];

/** 전체 증상 목록 (플랫). */
export const ALL_SYMPTOMS: SymptomItem[] = SYMPTOM_CATEGORIES.flatMap(
  (cat) => cat.symptoms,
);
