/**
 * 영양제 상세 페이지 폴백 콘텐츠 빌더.
 * API 데이터가 NULL인 필드에 대해 성분 매칭으로
 * 자동 콘텐츠를 생성합니다. 백엔드 변경 없이 thin content 해결.
 */

import type { SupplementDetail } from "@/types/supplement";
import type { IngredientInfo } from "@/types/drug";
import {
  matchIngredients,
  type MatchedIngredient,
} from "@/lib/utils/ingredientMatcher";
import type { FAQItem } from "@/lib/faq";

export interface SupplementFallbackContent {
  /** 매칭된 성분 가이드 목록 */
  matchedIngredients: MatchedIngredient[];
  /** 기능성 폴백 (functionality가 null일 때) */
  overview: string | null;
  /** 주의사항 폴백 (precautions가 null일 때) */
  fallbackPrecautions: string | null;
  /** 추가 FAQ 항목 (성분 기반) */
  additionalFAQs: FAQItem[];
  /** 성분 팁 합산 */
  tips: string[];
}

/** JSONB 성분 데이터를 IngredientInfo[]로 정규화 (페이지와 동일 로직). */
function normalizeIngredients(
  raw: Record<string, unknown>[] | null,
): IngredientInfo[] {
  if (!raw) return [];
  return raw.map((item) => ({
    name: String(item.name ?? item.ingredient_name ?? ""),
    amount: item.amount != null ? String(item.amount) : null,
    unit: item.unit != null ? String(item.unit) : null,
  }));
}

export function buildSupplementFallbackContent(
  supp: SupplementDetail,
): SupplementFallbackContent {
  const ingredients = normalizeIngredients(supp.ingredients);
  const matchedIngredients = matchIngredients(
    ingredients,
    supp.main_ingredient,
  );

  const overview = buildOverview(supp, matchedIngredients);
  const fallbackPrecautions = buildPrecautions(supp, matchedIngredients);
  const additionalFAQs = buildAdditionalFAQs(supp, matchedIngredients);
  const tips = buildTips(matchedIngredients);

  return {
    matchedIngredients,
    overview,
    fallbackPrecautions,
    additionalFAQs,
    tips,
  };
}

function buildOverview(
  supp: SupplementDetail,
  matched: MatchedIngredient[],
): string | null {
  if (supp.functionality) return null;
  if (matched.length === 0) return null;

  const parts: string[] = [];

  if (supp.category) {
    parts.push(
      `${supp.product_name}은(는) ${supp.category} 분야의 건강기능식품입니다.`,
    );
  }

  const summaries = matched
    .slice(0, 3)
    .map((m) => `${m.guide.name}: ${m.guide.summary}`)
    .join(" ");
  parts.push(summaries);

  return parts.join("\n\n");
}

function buildPrecautions(
  supp: SupplementDetail,
  matched: MatchedIngredient[],
): string | null {
  if (supp.precautions) return null;
  if (matched.length === 0) return null;

  const allInteractions: string[] = [];
  for (const m of matched.slice(0, 3)) {
    for (const interaction of m.guide.interactions) {
      allInteractions.push(`[${m.guide.name}] ${interaction}`);
    }
  }

  const allSideEffects: string[] = [];
  for (const m of matched.slice(0, 3)) {
    for (const effect of m.guide.sideEffects) {
      allSideEffects.push(`[${m.guide.name}] ${effect}`);
    }
  }

  const parts: string[] = [];
  if (allInteractions.length > 0) {
    parts.push(`성분별 알려진 상호작용:\n${allInteractions.join("\n")}`);
  }
  if (allSideEffects.length > 0) {
    parts.push(`성분별 알려진 부작용:\n${allSideEffects.join("\n")}`);
  }

  return parts.length > 0 ? parts.join("\n\n") : null;
}

function buildAdditionalFAQs(
  supp: SupplementDetail,
  matched: MatchedIngredient[],
): FAQItem[] {
  const faqs: FAQItem[] = [];

  for (const m of matched.slice(0, 3)) {
    if (m.guide.tips.length > 0) {
      faqs.push({
        question: `${m.guide.name} 성분 섭취 시 알아두면 좋은 점은?`,
        answer: m.guide.tips.join(" "),
      });
    }

    if (m.guide.interactions.length > 0) {
      faqs.push({
        question: `${m.guide.name}과 함께 먹으면 안 되는 것은?`,
        answer: m.guide.interactions.slice(0, 2).join(" "),
      });
    }
  }

  return faqs;
}

function buildTips(matched: MatchedIngredient[]): string[] {
  const tips: string[] = [];
  for (const m of matched.slice(0, 4)) {
    tips.push(...m.guide.tips.slice(0, 1));
  }
  return tips;
}
