import fs from "fs";
import path from "path";
import matter from "gray-matter";
import type { ContentTip, ContentNews, ContentResearch } from "./types";

/** content/ 루트 경로 (프로젝트 루트 기준). */
const CONTENT_ROOT = path.join(process.cwd(), "..", "..", "content");

/** 지정 타입의 모든 Markdown 파일을 읽어 파싱한다. */
function loadAll<T extends { slug: string; content: string; reviewStatus?: string }>(
  type: string,
): T[] {
  const dir = path.join(CONTENT_ROOT, type);
  if (!fs.existsSync(dir)) return [];

  return fs
    .readdirSync(dir)
    .filter((f) => f.endsWith(".md"))
    .map((f) => {
      const raw = fs.readFileSync(path.join(dir, f), "utf-8");
      const { data, content } = matter(raw);
      return { ...data, content: content.trim() } as T;
    })
    .filter((item) => item.reviewStatus === "published")
    .sort((a, b) => {
      const da = (a as unknown as { publishedAt?: string }).publishedAt ?? "";
      const db = (b as unknown as { publishedAt?: string }).publishedAt ?? "";
      return db.localeCompare(da);
    });
}

/** slug로 단일 항목을 찾는다. */
function loadBySlug<T extends { slug: string; content: string }>(
  type: string,
  slug: string,
): T | null {
  const filePath = path.join(CONTENT_ROOT, type, `${slug}.md`);
  if (!fs.existsSync(filePath)) return null;

  const raw = fs.readFileSync(filePath, "utf-8");
  const { data, content } = matter(raw);
  return { ...data, content: content.trim() } as T;
}

/** 지정 타입의 모든 published slug를 반환한다. */
function loadAllSlugs(type: string): string[] {
  return loadAll<{ slug: string; content: string; reviewStatus?: string }>(type).map(
    (item) => item.slug,
  );
}

/* ── 팁 ── */
export function getAllTips(): ContentTip[] {
  return loadAll<ContentTip>("tips");
}

export function getTipBySlug(slug: string): ContentTip | null {
  return loadBySlug<ContentTip>("tips", slug);
}

export function getAllTipSlugs(): string[] {
  return loadAllSlugs("tips");
}

/* ── 뉴스 ── */
export function getAllNews(): ContentNews[] {
  return loadAll<ContentNews>("news");
}

export function getNewsBySlug(slug: string): ContentNews | null {
  return loadBySlug<ContentNews>("news", slug);
}

export function getAllNewsSlugs(): string[] {
  return loadAllSlugs("news");
}

/* ── 연구 ── */
export function getAllResearch(): ContentResearch[] {
  return loadAll<ContentResearch>("research");
}

export function getResearchBySlug(slug: string): ContentResearch | null {
  return loadBySlug<ContentResearch>("research", slug);
}

export function getAllResearchSlugs(): string[] {
  return loadAllSlugs("research");
}
