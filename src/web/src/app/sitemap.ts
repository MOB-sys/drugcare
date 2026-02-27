import type { MetadataRoute } from "next";
import { getAllDrugSlugs } from "@/lib/api/drugs";
import { getAllSupplementSlugs } from "@/lib/api/supplements";
import { getAllTipSlugs } from "@/lib/data/tips";
import { ALL_LETTERS } from "@/lib/utils/korean";

const BASE_URL = process.env.NEXT_PUBLIC_SITE_URL || "https://pillright.com";

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const staticPages: MetadataRoute.Sitemap = [
    { url: BASE_URL, lastModified: new Date(), changeFrequency: "daily", priority: 1.0 },
    { url: `${BASE_URL}/check`, lastModified: new Date(), changeFrequency: "weekly", priority: 0.9 },
    { url: `${BASE_URL}/drugs`, lastModified: new Date(), changeFrequency: "weekly", priority: 0.8 },
    { url: `${BASE_URL}/supplements`, lastModified: new Date(), changeFrequency: "weekly", priority: 0.8 },
    { url: `${BASE_URL}/compare`, lastModified: new Date(), changeFrequency: "weekly", priority: 0.7 },
    { url: `${BASE_URL}/privacy`, lastModified: new Date(), changeFrequency: "yearly", priority: 0.3 },
    { url: `${BASE_URL}/terms`, lastModified: new Date(), changeFrequency: "yearly", priority: 0.3 },
    { url: `${BASE_URL}/contact`, lastModified: new Date(), changeFrequency: "yearly", priority: 0.4 },
  ];

  let drugEntries: MetadataRoute.Sitemap = [];
  let suppEntries: MetadataRoute.Sitemap = [];

  try {
    const drugSlugs = await getAllDrugSlugs();
    drugEntries = drugSlugs.map((slug) => ({
      url: `${BASE_URL}/drugs/${slug}`,
      changeFrequency: "monthly" as const,
      priority: 0.7,
    }));
  } catch {
    /* 빌드 시 API 미연결이면 빈 배열 */
  }

  try {
    const suppSlugs = await getAllSupplementSlugs();
    suppEntries = suppSlugs.map((slug) => ({
      url: `${BASE_URL}/supplements/${slug}`,
      changeFrequency: "monthly" as const,
      priority: 0.7,
    }));
  } catch {
    /* 빌드 시 API 미연결이면 빈 배열 */
  }

  const tipEntries: MetadataRoute.Sitemap = [
    { url: `${BASE_URL}/tips`, changeFrequency: "weekly" as const, priority: 0.8 },
    ...getAllTipSlugs().map((slug) => ({
      url: `${BASE_URL}/tips/${slug}`,
      changeFrequency: "monthly" as const,
      priority: 0.6,
    })),
  ];

  /* A~Z 브라우즈 페이지 — 내부 링크 강화 */
  const browseEntries: MetadataRoute.Sitemap = ALL_LETTERS.flatMap((letter) => [
    { url: `${BASE_URL}/drugs/browse/${encodeURIComponent(letter)}`, changeFrequency: "weekly" as const, priority: 0.6 },
    { url: `${BASE_URL}/supplements/browse/${encodeURIComponent(letter)}`, changeFrequency: "weekly" as const, priority: 0.6 },
  ]);

  return [...staticPages, ...browseEntries, ...tipEntries, ...drugEntries, ...suppEntries];
}
