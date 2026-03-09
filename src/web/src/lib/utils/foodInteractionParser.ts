/** Extract food-related interactions from intrc_qesitm text. */

import { FOOD_KEYWORDS, FOOD_KEYWORD_LIST, type FoodInfo } from "@/lib/data/foodKeywords";

export interface FoodInteraction {
  food: FoodInfo;
  contextText: string;
}

/** Extract surrounding sentence for a keyword match. */
function extractContext(text: string, keyword: string): string {
  const idx = text.indexOf(keyword);
  if (idx === -1) return "";

  const sentenceBreaks = /[.!?。]\s*/;
  const before = text.slice(0, idx);
  const after = text.slice(idx);

  const startMatch = before.match(/(?:.*[.!?。]\s*)?([^.!?。]*)$/);
  const start = startMatch ? before.length - startMatch[1].length : Math.max(0, idx - 80);

  const endMatch = after.match(sentenceBreaks);
  const end = endMatch ? idx + (endMatch.index ?? 0) + endMatch[0].length : Math.min(text.length, idx + 120);

  return text.slice(start, end).trim();
}

/** Parse intrc_qesitm text and return matched food interactions. */
export function parseFoodInteractions(text: string | null): FoodInteraction[] {
  if (!text) return [];

  const found: FoodInteraction[] = [];
  const seenCategories = new Set<string>();

  for (const keyword of FOOD_KEYWORD_LIST) {
    if (!text.includes(keyword)) continue;

    const food = FOOD_KEYWORDS[keyword];
    const categoryKey = `${food.category}-${food.name}`;
    if (seenCategories.has(categoryKey)) continue;
    seenCategories.add(categoryKey);

    const contextText = extractContext(text, keyword);
    found.push({ food, contextText });
  }

  return found;
}
