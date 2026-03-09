/** Static mapping of food names to display info and categories. */

export interface FoodInfo {
  name: string;
  icon: string;
  category: "fruit" | "dairy" | "beverage" | "alcohol" | "meal" | "other";
  categoryLabel: string;
}

export const FOOD_KEYWORDS: Record<string, FoodInfo> = {
  "자몽": { name: "자몽", icon: "🍊", category: "fruit", categoryLabel: "과일" },
  "자몽주스": { name: "자몽주스", icon: "🧃", category: "fruit", categoryLabel: "과일" },
  "우유": { name: "우유", icon: "🥛", category: "dairy", categoryLabel: "유제품" },
  "유제품": { name: "유제품", icon: "🧀", category: "dairy", categoryLabel: "유제품" },
  "치즈": { name: "치즈", icon: "🧀", category: "dairy", categoryLabel: "유제품" },
  "요구르트": { name: "요구르트", icon: "🥛", category: "dairy", categoryLabel: "유제품" },
  "알코올": { name: "알코올", icon: "🍺", category: "alcohol", categoryLabel: "주류" },
  "음주": { name: "음주", icon: "🍺", category: "alcohol", categoryLabel: "주류" },
  "주류": { name: "주류", icon: "🍾", category: "alcohol", categoryLabel: "주류" },
  "술": { name: "술", icon: "🍶", category: "alcohol", categoryLabel: "주류" },
  "카페인": { name: "카페인", icon: "☕", category: "beverage", categoryLabel: "음료" },
  "커피": { name: "커피", icon: "☕", category: "beverage", categoryLabel: "음료" },
  "녹차": { name: "녹차", icon: "🍵", category: "beverage", categoryLabel: "음료" },
  "차": { name: "차", icon: "🍵", category: "beverage", categoryLabel: "음료" },
  "식사": { name: "식사", icon: "🍚", category: "meal", categoryLabel: "식사" },
  "음식": { name: "음식", icon: "🍜", category: "meal", categoryLabel: "식사" },
  "과일": { name: "과일", icon: "🍎", category: "fruit", categoryLabel: "과일" },
  "바나나": { name: "바나나", icon: "🍌", category: "fruit", categoryLabel: "과일" },
  "오렌지": { name: "오렌지", icon: "🍊", category: "fruit", categoryLabel: "과일" },
  "칼슘": { name: "칼슘", icon: "🥛", category: "dairy", categoryLabel: "유제품" },
  "철분": { name: "철분", icon: "🧊", category: "other", categoryLabel: "기타" },
  "비타민 K": { name: "비타민 K", icon: "🥦", category: "other", categoryLabel: "기타" },
  "시금치": { name: "시금치", icon: "🥬", category: "other", categoryLabel: "기타" },
  "브로콜리": { name: "브로콜리", icon: "🥦", category: "other", categoryLabel: "기타" },
  "고지방": { name: "고지방 식사", icon: "🍔", category: "meal", categoryLabel: "식사" },
  "인삼": { name: "인삼", icon: "🌿", category: "other", categoryLabel: "기타" },
  "마늘": { name: "마늘", icon: "🧄", category: "other", categoryLabel: "기타" },
};

/** All food keyword strings for matching. */
export const FOOD_KEYWORD_LIST = Object.keys(FOOD_KEYWORDS);
