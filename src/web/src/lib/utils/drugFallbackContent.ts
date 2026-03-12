/**
 * 약물 상세 페이지 폴백 콘텐츠 빌더.
 * API 데이터가 NULL인 필드에 대해 성분 매칭 + 분류 매칭으로
 * 자동 콘텐츠를 생성합니다. 백엔드 변경 없이 thin content 해결.
 */

import type { DrugDetail } from "@/types/drug";
import type { DrugCategory } from "@/lib/data/drugCategories";
import { getCategoryForClassNo } from "@/lib/data/classNoMapping";
import {
  matchIngredients,
  type MatchedIngredient,
} from "@/lib/utils/ingredientMatcher";
import type { FAQItem } from "@/lib/faq";

export interface DrugFallbackContent {
  /** 매칭된 분류 정보 */
  category: DrugCategory | undefined;
  /** 매칭된 성분 가이드 목록 */
  matchedIngredients: MatchedIngredient[];
  /** 효능·효과 폴백 (efcy_qesitm이 null일 때) */
  overview: string | null;
  /** 부작용 폴백 (se_qesitm이 null일 때) */
  fallbackSideEffects: string | null;
  /** 상호작용 폴백 (intrc_qesitm이 null일 때) */
  fallbackInteractions: string | null;
  /** 추가 FAQ 항목 (분류/성분 기반) */
  additionalFAQs: FAQItem[];
  /** 분류 주의사항 + 성분 팁 합산 */
  tips: string[];
}

export function buildDrugFallbackContent(
  drug: DrugDetail,
): DrugFallbackContent {
  const category = getCategoryForClassNo(drug.class_no);
  const matchedIngredients = matchIngredients(
    drug.ingredients,
    drug.material_name,
  );

  const overview = buildOverview(drug, category, matchedIngredients);
  const fallbackSideEffects = buildSideEffects(drug, matchedIngredients);
  const fallbackInteractions = buildInteractions(drug, matchedIngredients);
  const additionalFAQs = buildAdditionalFAQs(
    drug,
    category,
    matchedIngredients,
  );
  const tips = buildTips(category, matchedIngredients);

  return {
    category,
    matchedIngredients,
    overview,
    fallbackSideEffects,
    fallbackInteractions,
    additionalFAQs,
    tips,
  };
}

function buildOverview(
  drug: DrugDetail,
  category: DrugCategory | undefined,
  matched: MatchedIngredient[],
): string | null {
  if (drug.efcy_qesitm) return null; // API 데이터가 있으면 폴백 불필요

  const parts: string[] = [];

  if (category) {
    parts.push(
      `${drug.item_name}은(는) ${category.name} 계열의 의약품입니다. ${category.description}`,
    );
  }

  if (matched.length > 0) {
    const ingredientSummaries = matched
      .slice(0, 3)
      .map((m) => `${m.guide.name}: ${m.guide.summary}`)
      .join(" ");
    parts.push(ingredientSummaries);
  }

  return parts.length > 0 ? parts.join("\n\n") : null;
}

function buildSideEffects(
  drug: DrugDetail,
  matched: MatchedIngredient[],
): string | null {
  if (drug.se_qesitm) return null;
  if (matched.length === 0) return null;

  const allEffects: string[] = [];
  for (const m of matched.slice(0, 3)) {
    for (const effect of m.guide.sideEffects) {
      allEffects.push(`[${m.guide.name}] ${effect}`);
    }
  }

  return allEffects.length > 0
    ? `주요 성분별 알려진 부작용:\n${allEffects.join("\n")}`
    : null;
}

function buildInteractions(
  drug: DrugDetail,
  matched: MatchedIngredient[],
): string | null {
  if (drug.intrc_qesitm) return null;
  if (matched.length === 0) return null;

  const allInteractions: string[] = [];
  for (const m of matched.slice(0, 3)) {
    for (const interaction of m.guide.interactions) {
      allInteractions.push(`[${m.guide.name}] ${interaction}`);
    }
  }

  return allInteractions.length > 0
    ? `주요 성분별 알려진 상호작용:\n${allInteractions.join("\n")}`
    : null;
}

function buildAdditionalFAQs(
  drug: DrugDetail,
  category: DrugCategory | undefined,
  matched: MatchedIngredient[],
): FAQItem[] {
  const faqs: FAQItem[] = [];

  if (category) {
    faqs.push({
      question: `${drug.item_name}은(는) 어떤 종류의 약인가요?`,
      answer: `${drug.item_name}은(는) ${category.name} 계열의 의약품입니다. ${category.description}`,
    });
  }

  for (const m of matched.slice(0, 2)) {
    if (m.guide.tips.length > 0) {
      faqs.push({
        question: `${m.guide.name} 성분 복용 시 알아두면 좋은 점은?`,
        answer: m.guide.tips.join(" "),
      });
    }
  }

  if (category && category.precautions.length > 0) {
    faqs.push({
      question: `${category.name} 약물 복용 시 주의사항은?`,
      answer: category.precautions.slice(0, 3).join(" "),
    });
  }

  return faqs;
}

function buildTips(
  category: DrugCategory | undefined,
  matched: MatchedIngredient[],
): string[] {
  const tips: string[] = [];

  if (category) {
    tips.push(...category.precautions.slice(0, 2));
  }

  for (const m of matched.slice(0, 3)) {
    tips.push(...m.guide.tips.slice(0, 1));
  }

  return tips;
}
