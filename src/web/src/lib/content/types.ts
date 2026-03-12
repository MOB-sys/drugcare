/** 콘텐츠 공통 frontmatter 타입. */
export interface ContentMeta {
  slug: string;
  title: string;
  description: string;
  tags: string[];
  category?: string;
  source: "editorial" | "pubmed" | "mfds" | "fda" | "ai_generated";
  publishedAt: string;
  updatedAt?: string;
  reviewStatus: "draft" | "review" | "published";
}

/** 건강팁 (기존 Tip 인터페이스 대체). */
export interface ContentTip extends ContentMeta {
  content: string;
}

/** 뉴스/안전 경고. */
export interface ContentNews extends ContentMeta {
  content: string;
  sourceUrl?: string;
  severity?: "info" | "warning" | "danger";
  relatedDrugs?: string[];
}

/** 연구 요약. */
export interface ContentResearch extends ContentMeta {
  content: string;
  pubmedId?: string;
  doi?: string;
  authors?: string[];
  journal?: string;
  relatedIngredients?: string[];
  evidenceLevel?: "high" | "moderate" | "low";
}
