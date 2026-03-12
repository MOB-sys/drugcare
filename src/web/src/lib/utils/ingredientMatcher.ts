/**
 * 약물 성분 ↔ ingredients.ts 가이드 매칭 유틸리티.
 * drug.ingredients[].name 및 material_name 텍스트에서
 * 20개 성분 가이드와 매칭하여 폴백 콘텐츠를 생성합니다.
 */

import { ingredients, type IngredientGuide } from "@/lib/data/ingredients";
import type { IngredientInfo } from "@/types/drug";

export interface MatchedIngredient {
  guide: IngredientGuide;
  matchedName: string; // 매칭된 원래 성분명
}

/** 성분명 정규화: 소문자 + 공백/하이픈 제거 + 접미사 제거 */
function normalize(name: string): string {
  return name
    .toLowerCase()
    .replace(/[\s\-·・]/g, "")
    .replace(/(정|캡슐|산$|염$|수화물$|나트륨$|칼륨$|칼슘$|마그네슘$)/g, "")
    .trim();
}

/** 한글/영문 양방향 매칭 테이블 */
const matchPatterns: { guide: IngredientGuide; patterns: string[] }[] =
  ingredients.map((g) => ({
    guide: g,
    patterns: [
      normalize(g.name),
      normalize(g.nameEn),
      // 추가 별칭
      ...(g.slug === "acetaminophen"
        ? ["파라세타몰", "paracetamol"].map(normalize)
        : []),
      ...(g.slug === "aspirin"
        ? ["아세틸살리실산", "acetylsalicylicacid"].map(normalize)
        : []),
      ...(g.slug === "omega-3"
        ? ["epa", "dha", "이코사펜트산", "도코사헥사엔산"].map(normalize)
        : []),
      ...(g.slug === "vitamin-c"
        ? ["아스코르브산", "ascorbicacid"].map(normalize)
        : []),
      ...(g.slug === "vitamin-d"
        ? [
            "콜레칼시페롤",
            "cholecalciferol",
            "에르고칼시페롤",
            "ergocalciferol",
          ].map(normalize)
        : []),
      ...(g.slug === "vitamin-b12"
        ? ["코발라민", "cobalamin", "메코발라민", "mecobalamin"].map(normalize)
        : []),
      ...(g.slug === "folic-acid"
        ? ["폴산", "엽산", "folate", "메틸폴레이트"].map(normalize)
        : []),
      ...(g.slug === "probiotics"
        ? ["유산균", "락토바실러스", "비피도박테리움", "lactobacillus"].map(
            normalize,
          )
        : []),
      ...(g.slug === "iron"
        ? ["황산제일철", "ferrousfumarate", "ferrousSulfate"].map(normalize)
        : []),
      ...(g.slug === "calcium"
        ? ["탄산칼슘", "구연산칼슘", "calciumcarbonate"].map(normalize)
        : []),
      ...(g.slug === "magnesium"
        ? ["산화마그네슘", "구연산마그네슘", "magnesiumoxide"].map(normalize)
        : []),
      ...(g.slug === "zinc"
        ? ["산화아연", "황산아연", "zincoxide"].map(normalize)
        : []),
      ...(g.slug === "coq10"
        ? ["유비퀴논", "ubiquinone", "유비퀴놀", "ubiquinol"].map(normalize)
        : []),
      ...(g.slug === "glucosamine"
        ? ["글루코사민황산", "glucosaminesulfate"].map(normalize)
        : []),
      ...(g.slug === "milk-thistle"
        ? ["실리마린", "silymarin"].map(normalize)
        : []),
      ...(g.slug === "lutein" ? ["지아잔틴", "zeaxanthin"].map(normalize) : []),
    ],
  }));

/** 성분 이름이 가이드 패턴에 포함되는지 확인 */
function findMatch(name: string): IngredientGuide | undefined {
  const n = normalize(name);
  if (!n) return undefined;

  for (const { guide, patterns } of matchPatterns) {
    for (const p of patterns) {
      if (n.includes(p) || p.includes(n)) {
        return guide;
      }
    }
  }
  return undefined;
}

/**
 * 약물의 성분 목록과 material_name에서 가이드 매칭.
 * 중복 제거하여 고유한 매칭만 반환합니다.
 */
export function matchIngredients(
  ingredientsList: IngredientInfo[] | null,
  materialName: string | null,
): MatchedIngredient[] {
  const matched = new Map<string, MatchedIngredient>();

  // 1) ingredients 배열에서 매칭
  if (ingredientsList) {
    for (const ing of ingredientsList) {
      const guide = findMatch(ing.name);
      if (guide && !matched.has(guide.slug)) {
        matched.set(guide.slug, { guide, matchedName: ing.name });
      }
    }
  }

  // 2) material_name 텍스트에서 추가 매칭
  if (materialName) {
    // material_name은 "성분1|성분2|..." 또는 쉼표 구분
    const parts = materialName.split(/[|,;]/);
    for (const part of parts) {
      const name = part.trim();
      if (!name) continue;
      const guide = findMatch(name);
      if (guide && !matched.has(guide.slug)) {
        matched.set(guide.slug, { guide, matchedName: name });
      }
    }
  }

  return Array.from(matched.values());
}
