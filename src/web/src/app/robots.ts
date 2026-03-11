import type { MetadataRoute } from "next";
import { SITE_URL } from "@/lib/constants/site";

const BASE_URL = SITE_URL;

export default function robots(): MetadataRoute.Robots {
  return {
    rules: {
      userAgent: "*",
      allow: "/",
      disallow: ["/api/", "/cabinet", "/check/result"],
    },
    sitemap: `${BASE_URL}/sitemap.xml`,
  };
}
