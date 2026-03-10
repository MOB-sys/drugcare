import Link from "next/link";
import { tips } from "@/lib/data/tips";
import type { Tip } from "@/lib/data/tips";

interface RelatedTipsProps {
  /** Drug name or keywords used for matching tips. */
  drugName: string;
  /** Optional drug category code for broader matching. */
  classNo?: string | null;
}

function findRelatedTips(drugName: string, classNo?: string | null): Tip[] {
  const nameLower = drugName.toLowerCase();

  // Score each tip based on keyword overlap with drug name and tags
  const scored = tips.map((tip) => {
    let score = 0;
    const titleLower = tip.title.toLowerCase();
    const descLower = tip.description.toLowerCase();
    const tagsJoined = tip.tags.join(" ").toLowerCase();

    // Check if drug name appears in tip content
    if (titleLower.includes(nameLower) || descLower.includes(nameLower)) {
      score += 10;
    }
    if (tagsJoined.includes(nameLower)) {
      score += 5;
    }

    // Check individual words from drug name (at least 2 chars)
    const words = nameLower.split(/\s+/).filter((w) => w.length >= 2);
    for (const word of words) {
      if (titleLower.includes(word) || tagsJoined.includes(word)) {
        score += 3;
      }
      if (descLower.includes(word)) {
        score += 1;
      }
    }

    // General keyword matching for common drug categories
    const categoryKeywords: Record<string, string[]> = {
      "혈압": ["혈압약", "고혈압"],
      "당뇨": ["당뇨약", "메트포르민"],
      "항생": ["항생제"],
      "진통": ["진통제", "소염"],
      "비타민": ["비타민", "영양제"],
      "오메가": ["오메가3", "오메가-3"],
    };

    for (const [keyword, matchTerms] of Object.entries(categoryKeywords)) {
      if (nameLower.includes(keyword)) {
        for (const term of matchTerms) {
          if (tagsJoined.includes(term.toLowerCase()) || titleLower.includes(term.toLowerCase())) {
            score += 4;
          }
        }
      }
    }

    return { tip, score };
  });

  // Sort by score descending, take top 3 with score > 0
  const matched = scored
    .filter((s) => s.score > 0)
    .sort((a, b) => b.score - a.score)
    .slice(0, 3)
    .map((s) => s.tip);

  // If no match, return first 2 tips as general recommendations
  if (matched.length === 0) {
    return tips.slice(0, 2);
  }

  return matched;
}

export function RelatedTips({ drugName, classNo }: RelatedTipsProps) {
  const relatedTips = findRelatedTips(drugName, classNo);

  if (relatedTips.length === 0) return null;

  return (
    <section className="mt-8">
      <h2 className="text-lg font-semibold text-[var(--color-primary)] mb-3">
        관련 건강팁
      </h2>
      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
        {relatedTips.map((tip) => (
          <Link
            key={tip.slug}
            href={`/tips/${tip.slug}`}
            className="group block p-4 bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-700 hover:border-[var(--color-primary-100)] hover:shadow-sm transition-all"
          >
            <h3 className="text-sm font-medium text-gray-900 dark:text-gray-100 mb-1.5 line-clamp-2 group-hover:text-[var(--color-primary)] transition-colors">
              {tip.title}
            </h3>
            <p className="text-xs text-gray-500 dark:text-gray-400 line-clamp-2 mb-2">
              {tip.description}
            </p>
            <span className="text-xs font-medium text-[var(--color-primary)] group-hover:underline">
              자세히 보기 →
            </span>
          </Link>
        ))}
      </div>
    </section>
  );
}
