import type { MetadataRoute } from "next";
import { getAllDrugSlugs } from "@/lib/api/drugs";
import { getAllSupplementSlugs } from "@/lib/api/supplements";
import { getAllTipSlugs } from "@/lib/data/tips";

const BASE_URL = process.env.NEXT_PUBLIC_SITE_URL || "https://yakmeogeo.com";

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const staticPages: MetadataRoute.Sitemap = [
    { url: BASE_URL, lastModified: new Date(), changeFrequency: "daily", priority: 1.0 },
    { url: `${BASE_URL}/check`, lastModified: new Date(), changeFrequency: "weekly", priority: 0.9 },
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

  return [...staticPages, ...tipEntries, ...drugEntries, ...suppEntries];
}
