import type { MetadataRoute } from "next";
import { getAllDrugSlugs } from "@/lib/api/drugs";
import { getAllSupplementSlugs } from "@/lib/api/supplements";
import { getAllFoodSlugs } from "@/lib/api/foods";
import { getAllHerbalMedicineSlugs } from "@/lib/api/herbal";
import { getAllTipSlugs, getAllNewsSlugs, getAllResearchSlugs } from "@/lib/content/loader";
import { ALL_LETTERS } from "@/lib/utils/korean";
import { SITE_URL } from "@/lib/constants/site";
import snsIndex from "../../public/sns-content/index.json";

const BASE_URL = SITE_URL;
const SITEMAP_LIMIT = 45000;

/** 대량 slug 배열을 45,000건씩 청크로 나눈다. */
function chunk<T>(arr: T[], size: number): T[][] {
  const result: T[][] = [];
  for (let i = 0; i < arr.length; i += size) {
    result.push(arr.slice(i, i + size));
  }
  return result;
}

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  /* ── 정적 페이지 ── */
  const staticPages: MetadataRoute.Sitemap = [
    { url: BASE_URL, lastModified: new Date(), changeFrequency: "daily", priority: 1.0 },
    { url: `${BASE_URL}/check`, lastModified: new Date(), changeFrequency: "weekly", priority: 0.9 },
    { url: `${BASE_URL}/compare`, lastModified: new Date(), changeFrequency: "weekly", priority: 0.7 },
    { url: `${BASE_URL}/drugs`, lastModified: new Date(), changeFrequency: "weekly", priority: 0.8 },
    { url: `${BASE_URL}/supplements`, lastModified: new Date(), changeFrequency: "weekly", priority: 0.8 },
    { url: `${BASE_URL}/foods`, lastModified: new Date(), changeFrequency: "weekly", priority: 0.8 },
    { url: `${BASE_URL}/herbal-medicines`, lastModified: new Date(), changeFrequency: "weekly", priority: 0.8 },
    { url: `${BASE_URL}/symptoms`, lastModified: new Date(), changeFrequency: "monthly", priority: 0.6 },
    { url: `${BASE_URL}/drugs/identify`, lastModified: new Date(), changeFrequency: "monthly", priority: 0.6 },
    { url: `${BASE_URL}/drugs/side-effects`, lastModified: new Date(), changeFrequency: "monthly", priority: 0.6 },
    { url: `${BASE_URL}/drugs/conditions`, lastModified: new Date(), changeFrequency: "monthly", priority: 0.6 },
    { url: `${BASE_URL}/privacy`, lastModified: new Date(), changeFrequency: "yearly", priority: 0.3 },
    { url: `${BASE_URL}/terms`, lastModified: new Date(), changeFrequency: "yearly", priority: 0.3 },
    { url: `${BASE_URL}/contact`, lastModified: new Date(), changeFrequency: "yearly", priority: 0.4 },
  ];

  /* ── 안전 카드 ── */
  const safetyCardEntries: MetadataRoute.Sitemap = [
    { url: `${BASE_URL}/safety-cards`, changeFrequency: "weekly" as const, priority: 0.8 },
    ...snsIndex.items.map((item: { id: string }) => ({
      url: `${BASE_URL}/safety-cards/${item.id}`,
      changeFrequency: "monthly" as const,
      priority: 0.7,
    })),
  ];

  /* ── A~Z 브라우즈 ── */
  const browseEntries: MetadataRoute.Sitemap = ALL_LETTERS.flatMap((letter) => [
    { url: `${BASE_URL}/drugs/browse/${encodeURIComponent(letter)}`, changeFrequency: "weekly" as const, priority: 0.6 },
    { url: `${BASE_URL}/supplements/browse/${encodeURIComponent(letter)}`, changeFrequency: "weekly" as const, priority: 0.6 },
  ]);

  /* ── 팁 ── */
  const tipEntries: MetadataRoute.Sitemap = [
    { url: `${BASE_URL}/tips`, changeFrequency: "weekly" as const, priority: 0.8 },
    ...getAllTipSlugs().map((slug) => ({
      url: `${BASE_URL}/tips/${slug}`,
      changeFrequency: "monthly" as const,
      priority: 0.6,
    })),
  ];

  /* ── 뉴스 + 연구 ── */
  const newsEntries: MetadataRoute.Sitemap = [
    ...getAllNewsSlugs().map((slug) => ({
      url: `${BASE_URL}/news/${slug}`,
      changeFrequency: "monthly" as const,
      priority: 0.6,
    })),
  ];
  const researchEntries: MetadataRoute.Sitemap = [
    { url: `${BASE_URL}/research`, changeFrequency: "weekly" as const, priority: 0.7 },
    ...getAllResearchSlugs().map((slug) => ({
      url: `${BASE_URL}/research/${slug}`,
      changeFrequency: "monthly" as const,
      priority: 0.6,
    })),
  ];

  /* ── 식품 + 한약재 (소량 — 항상 포함) ── */
  let foodEntries: MetadataRoute.Sitemap = [];
  let herbalEntries: MetadataRoute.Sitemap = [];
  try {
    const foodSlugs = await getAllFoodSlugs();
    foodEntries = foodSlugs.map((slug) => ({
      url: `${BASE_URL}/foods/${slug}`,
      changeFrequency: "monthly" as const,
      priority: 0.7,
    }));
  } catch { /* API 미연결 대비 */ }

  try {
    const herbalSlugs = await getAllHerbalMedicineSlugs();
    herbalEntries = herbalSlugs.map((slug) => ({
      url: `${BASE_URL}/herbal-medicines/${slug}`,
      changeFrequency: "monthly" as const,
      priority: 0.7,
    }));
  } catch { /* API 미연결 대비 */ }

  /* ── 약물 (대량 — 45K씩 분할) ── */
  let drugEntries: MetadataRoute.Sitemap = [];
  try {
    const drugSlugs = await getAllDrugSlugs();
    const drugChunks = chunk(drugSlugs, SITEMAP_LIMIT);
    // 첫 청크만 이 사이트맵에 포함 (50K 한도 준수)
    if (drugChunks.length > 0) {
      drugEntries = drugChunks[0].map((slug) => ({
        url: `${BASE_URL}/drugs/${slug}`,
        changeFrequency: "monthly" as const,
        priority: 0.7,
      }));
    }
  } catch { /* API 미연결 대비 */ }

  /* 현재까지 URL 수 계산 */
  const currentCount = staticPages.length + browseEntries.length + tipEntries.length
    + safetyCardEntries.length + newsEntries.length + researchEntries.length
    + foodEntries.length + herbalEntries.length + drugEntries.length;

  /* ── 영양제 (남은 한도만큼) ── */
  let suppEntries: MetadataRoute.Sitemap = [];
  const remaining = SITEMAP_LIMIT - currentCount;
  try {
    const suppSlugs = await getAllSupplementSlugs();
    const limitedSlugs = suppSlugs.slice(0, Math.max(0, remaining));
    suppEntries = limitedSlugs.map((slug) => ({
      url: `${BASE_URL}/supplements/${slug}`,
      changeFrequency: "monthly" as const,
      priority: 0.7,
    }));
  } catch { /* API 미연결 대비 */ }

  return [
    ...staticPages,
    ...browseEntries,
    ...tipEntries,
    ...safetyCardEntries,
    ...newsEntries,
    ...researchEntries,
    ...foodEntries,
    ...herbalEntries,
    ...drugEntries,
    ...suppEntries,
  ];
}
