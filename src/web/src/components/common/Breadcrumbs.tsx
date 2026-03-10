/** Breadcrumbs — SEO BreadcrumbList JSON-LD + 시각적 네비게이션. */

import Link from "next/link";
import { SITE_URL } from "@/lib/constants/site";

export interface BreadcrumbItem {
  label: string;
  href?: string;
}

interface BreadcrumbsProps {
  items: BreadcrumbItem[];
}

export function Breadcrumbs({ items }: BreadcrumbsProps) {
  const jsonLd = {
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    itemListElement: items.map((item, i) => ({
      "@type": "ListItem",
      position: i + 1,
      name: item.label,
      ...(item.href ? { item: `${SITE_URL}${item.href}` } : {}),
    })),
  };

  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
      />
      <nav aria-label="breadcrumb" className="max-w-5xl mx-auto px-4 pt-4 pb-1">
        <ol className="flex flex-wrap items-center gap-1 text-sm text-gray-500">
          {items.map((item, i) => (
            <li key={i} className="flex items-center gap-1">
              {i > 0 && (
                <svg className="w-3.5 h-3.5 text-gray-300 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                </svg>
              )}
              {item.href && i < items.length - 1 ? (
                <Link href={item.href} className="hover:text-[var(--color-primary)] transition-colors">
                  {item.label}
                </Link>
              ) : (
                <span className="text-gray-900 font-medium truncate max-w-[200px]" aria-current="page">{item.label}</span>
              )}
            </li>
          ))}
        </ol>
      </nav>
    </>
  );
}
