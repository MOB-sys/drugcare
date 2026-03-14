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

/**
 * 사이트맵당 최대 URL 수 — Google 한도는 50K이지만
 * 10K 이하로 유지해야 크롤링 효율이 좋다.
 */
const URLS_PER_SITEMAP = 10_000;

/** 대량 slug 배열을 size건씩 청크로 나눈다. */
function chunk<T>(arr: T[], size: number): T[][] {
  const result: T[][] = [];
  for (let i = 0; i < arr.length; i += size) {
    result.push(arr.slice(i, i + size));
  }
  return result;
}

/**
 * Next.js 15 sitemap index 지원.
 * 반환된 id 배열 수만큼 /sitemap/{id}.xml이 생성되고,
 * /sitemap.xml은 자동으로 sitemap index로 동작한다.
 *
 * 할당:
 *  - id 0 ~ N: 약물 (10K씩)
 *  - id N+1  : 영양제
 *  - id N+2  : 정적 + 식품 + 한약재 + 팁 + 뉴스 + 연구 + 안전카드 + 브라우즈
 */
export async function generateSitemaps() {
  let drugCount = 0;
  try {
    const slugs = await getAllDrugSlugs();
    drugCount = slugs.length;
  } catch { /* API 미연결 대비 */ }

  const drugSitemapCount = Math.max(1, Math.ceil(drugCount / URLS_PER_SITEMAP));

  const ids: { id: number }[] = [];
  for (let i = 0; i < drugSitemapCount; i++) {
    ids.push({ id: i }); // drugs
  }
  ids.push({ id: drugSitemapCount });     // supplements
  ids.push({ id: drugSitemapCount + 1 }); // misc (static + foods + herbals + tips + news + research + safety cards + browse)

  return ids;
}

export default async function sitemap({ id }: { id: number }): Promise<MetadataRoute.Sitemap> {
  /* ── 약물 사이트맵 개수 계산 (generateSitemaps와 동일 로직) ── */
  let drugSlugs: string[] = [];
  try {
    drugSlugs = await getAllDrugSlugs();
  } catch { /* API 미연결 대비 */ }
  const drugSitemapCount = Math.max(1, Math.ceil(drugSlugs.length / URLS_PER_SITEMAP));

  /* ── id < drugSitemapCount → 약물 사이트맵 ── */
  if (id < drugSitemapCount) {
    const drugChunks = chunk(drugSlugs, URLS_PER_SITEMAP);
    const slugsForId = drugChunks[id] ?? [];
    return slugsForId.map((slug) => ({
      url: `${BASE_URL}/drugs/${slug}`,
      changeFrequency: "monthly" as const,
      priority: 0.7,
    }));
  }

  /* ── 영양제 사이트맵 ── */
  if (id === drugSitemapCount) {
    let suppSlugs: string[] = [];
    try {
      suppSlugs = await getAllSupplementSlugs();
    } catch { /* API 미연결 대비 */ }
    return suppSlugs.map((slug) => ({
      url: `${BASE_URL}/supplements/${slug}`,
      changeFrequency: "monthly" as const,
      priority: 0.7,
    }));
  }

  /* ── 기타 (정적 + 식품 + 한약재 + 팁 + 뉴스 + 연구 + 안전카드 + 브라우즈) ── */
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

  const safetyCardEntries: MetadataRoute.Sitemap = [
    { url: `${BASE_URL}/safety-cards`, changeFrequency: "weekly" as const, priority: 0.8 },
    ...snsIndex.items.map((item: { id: string }) => ({
      url: `${BASE_URL}/safety-cards/${item.id}`,
      changeFrequency: "monthly" as const,
      priority: 0.7,
    })),
  ];

  const browseEntries: MetadataRoute.Sitemap = ALL_LETTERS.flatMap((letter) => [
    { url: `${BASE_URL}/drugs/browse/${encodeURIComponent(letter)}`, changeFrequency: "weekly" as const, priority: 0.6 },
    { url: `${BASE_URL}/supplements/browse/${encodeURIComponent(letter)}`, changeFrequency: "weekly" as const, priority: 0.6 },
  ]);

  const tipEntries: MetadataRoute.Sitemap = [
    { url: `${BASE_URL}/tips`, changeFrequency: "weekly" as const, priority: 0.8 },
    ...getAllTipSlugs().map((slug) => ({
      url: `${BASE_URL}/tips/${slug}`,
      changeFrequency: "monthly" as const,
      priority: 0.6,
    })),
  ];

  const newsEntries: MetadataRoute.Sitemap = getAllNewsSlugs().map((slug) => ({
    url: `${BASE_URL}/news/${slug}`,
    changeFrequency: "monthly" as const,
    priority: 0.6,
  }));

  const researchEntries: MetadataRoute.Sitemap = [
    { url: `${BASE_URL}/research`, changeFrequency: "weekly" as const, priority: 0.7 },
    ...getAllResearchSlugs().map((slug) => ({
      url: `${BASE_URL}/research/${slug}`,
      changeFrequency: "monthly" as const,
      priority: 0.6,
    })),
  ];

  let foodEntries: MetadataRoute.Sitemap = [];
  try {
    const foodSlugs = await getAllFoodSlugs();
    foodEntries = foodSlugs.map((slug) => ({
      url: `${BASE_URL}/foods/${slug}`,
      changeFrequency: "monthly" as const,
      priority: 0.7,
    }));
  } catch { /* API 미연결 대비 */ }

  let herbalEntries: MetadataRoute.Sitemap = [];
  try {
    const herbalSlugs = await getAllHerbalMedicineSlugs();
    herbalEntries = herbalSlugs.map((slug) => ({
      url: `${BASE_URL}/herbal-medicines/${slug}`,
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
  ];
}
