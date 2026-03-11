import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { getDrugBySlug } from "@/lib/api/drugs";
import { Breadcrumbs } from "@/components/common/Breadcrumbs";
import { AdBanner } from "@/components/ads/AdBanner";
import { SITE_URL } from "@/lib/constants/site";

interface PageProps {
  params: Promise<{ slug: string }>;
}

/* ── ISR ────────────────────────────────────────── */

export const dynamicParams = true;
export const revalidate = 86400; // 24시간

export async function generateStaticParams() {
  return [];
}

export async function generateMetadata({ params }: PageProps): Promise<Metadata> {
  const { slug } = await params;
  try {
    const drug = await getDrugBySlug(slug);
    const title = `${drug.item_name} 부작용 — 약잘알`;
    const description = drug.se_qesitm
      ? `${drug.item_name} 부작용 정보 — ${drug.se_qesitm.slice(0, 120)}`
      : `${drug.item_name} 부작용 정보를 확인하세요.`;
    return {
      title,
      description,
      openGraph: {
        title,
        description,
        type: "article",
        images: [
          {
            url: `${SITE_URL}/api/og?title=${encodeURIComponent(`${drug.item_name} 부작용`)}&type=drug`,
            width: 1200,
            height: 630,
            alt: title,
          },
        ],
      },
      twitter: {
        card: "summary_large_image",
        title,
        description,
      },
      alternates: { canonical: `/drugs/${slug}/side-effects` },
    };
  } catch {
    return { title: "부작용 정보" };
  }
}

/* ── 부작용 텍스트 파싱 ─────────────────────────── */

interface SideEffectGroup {
  category: "serious" | "common" | "other";
  label: string;
  items: string[];
}

const SERIOUS_KEYWORDS = ["즉시 중단", "의사", "응급", "심각", "사망", "아나필락시스", "호흡곤란", "쇼크", "중증"];
const COMMON_KEYWORDS = ["흔", "자주", "일반적", "흔히", "때때로", "가끔"];

function classifySentence(sentence: string): "serious" | "common" | "other" {
  const lower = sentence.toLowerCase();
  if (SERIOUS_KEYWORDS.some((kw) => lower.includes(kw))) return "serious";
  if (COMMON_KEYWORDS.some((kw) => lower.includes(kw))) return "common";
  return "other";
}

function parseSideEffects(text: string): SideEffectGroup[] {
  // Split by sentence endings or line breaks
  const sentences = text
    .split(/(?<=[.다])\s+|\n+/)
    .map((s) => s.trim())
    .filter((s) => s.length > 0);

  if (sentences.length === 0) return [];

  // If text is very short (1-2 sentences), don't categorize
  if (sentences.length <= 2) {
    return [{ category: "other", label: "부작용 정보", items: sentences }];
  }

  const serious: string[] = [];
  const common: string[] = [];
  const other: string[] = [];

  for (const sentence of sentences) {
    const cat = classifySentence(sentence);
    if (cat === "serious") serious.push(sentence);
    else if (cat === "common") common.push(sentence);
    else other.push(sentence);
  }

  const groups: SideEffectGroup[] = [];
  if (serious.length > 0) groups.push({ category: "serious", label: "심각한 부작용", items: serious });
  if (common.length > 0) groups.push({ category: "common", label: "흔한 부작용", items: common });
  if (other.length > 0) groups.push({ category: "other", label: "기타 부작용", items: other });

  return groups;
}

/* ── 카테고리별 스타일 ──────────────────────────── */

function getCategoryStyle(category: "serious" | "common" | "other") {
  switch (category) {
    case "serious":
      return {
        bg: "bg-red-50 dark:bg-red-950/30",
        border: "border-red-200 dark:border-red-800",
        iconColor: "text-red-600 dark:text-red-400",
        titleColor: "text-red-800 dark:text-red-300",
        textColor: "text-red-700 dark:text-red-300",
        dotColor: "bg-red-400 dark:bg-red-500",
      };
    case "common":
      return {
        bg: "bg-amber-50 dark:bg-amber-950/30",
        border: "border-amber-200 dark:border-amber-800",
        iconColor: "text-amber-600 dark:text-amber-400",
        titleColor: "text-amber-800 dark:text-amber-300",
        textColor: "text-amber-700 dark:text-amber-300",
        dotColor: "bg-amber-400 dark:bg-amber-500",
      };
    case "other":
      return {
        bg: "bg-gray-50 dark:bg-gray-800/50",
        border: "border-gray-200 dark:border-gray-700",
        iconColor: "text-gray-500 dark:text-gray-400",
        titleColor: "text-gray-800 dark:text-gray-200",
        textColor: "text-gray-700 dark:text-gray-300",
        dotColor: "bg-gray-400 dark:bg-gray-500",
      };
  }
}

function getCategoryIcon(category: "serious" | "common" | "other") {
  switch (category) {
    case "serious":
      return (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z" />
        </svg>
      );
    case "common":
      return (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      );
    case "other":
      return (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
        </svg>
      );
  }
}

/* ── Page ───────────────────────────────────────── */

export default async function DrugSideEffectsPage({ params }: PageProps) {
  const { slug } = await params;
  let drug;
  try {
    drug = await getDrugBySlug(slug);
  } catch {
    notFound();
  }

  const hasSideEffects = drug.se_qesitm && drug.se_qesitm.trim().length > 0;
  const groups = hasSideEffects ? parseSideEffects(drug.se_qesitm!) : [];

  const jsonLd = {
    "@context": "https://schema.org",
    "@type": "MedicalWebPage",
    name: `${drug.item_name} 부작용`,
    about: {
      "@type": "Drug",
      name: drug.item_name,
    },
    description: drug.se_qesitm ?? `${drug.item_name} 부작용 정보`,
    lastReviewed: new Date().toISOString().split("T")[0],
    medicalAudience: {
      "@type": "MedicalAudience",
      audienceType: "Patient",
    },
  };

  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd).replace(/</g, "\\u003c") }}
      />

      <Breadcrumbs
        items={[
          { label: "홈", href: "/" },
          { label: "의약품", href: "/drugs" },
          { label: drug.item_name, href: `/drugs/${slug}` },
          { label: "부작용" },
        ]}
      />

      <div className="max-w-3xl mx-auto px-4 py-6">
        {/* 헤더 */}
        <header className="mb-6">
          <h1 className="text-2xl font-bold text-[var(--color-primary)] mb-2 break-keep">
            {drug.item_name} 부작용 정보
          </h1>
          {drug.entp_name && (
            <p className="text-sm text-gray-500 dark:text-gray-400">{drug.entp_name}</p>
          )}
        </header>

        {hasSideEffects ? (
          <>
            {/* 부작용 그룹별 표시 */}
            <div className="space-y-4 mb-8">
              {groups.map((group) => {
                const style = getCategoryStyle(group.category);
                const icon = getCategoryIcon(group.category);
                return (
                  <section
                    key={group.category}
                    className={`rounded-xl border p-5 ${style.bg} ${style.border}`}
                  >
                    <div className="flex items-center gap-2 mb-3">
                      <span className={style.iconColor}>{icon}</span>
                      <h2 className={`text-base font-semibold ${style.titleColor}`}>
                        {group.label}
                      </h2>
                    </div>
                    <ul className="space-y-2">
                      {group.items.map((item, i) => (
                        <li key={i} className="flex items-start gap-2">
                          <span className={`w-1.5 h-1.5 rounded-full mt-2 shrink-0 ${style.dotColor}`} />
                          <span className={`${style.textColor} leading-relaxed break-keep`}>{item}</span>
                        </li>
                      ))}
                    </ul>
                  </section>
                );
              })}
            </div>

            {/* 대처 방법 안내 */}
            <section className="bg-blue-50 dark:bg-blue-950/30 border border-blue-200 dark:border-blue-800 rounded-xl p-5 mb-8">
              <div className="flex items-center gap-2 mb-3">
                <svg className="w-5 h-5 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                </svg>
                <h2 className="text-base font-semibold text-blue-800 dark:text-blue-300">
                  부작용 대처 방법
                </h2>
              </div>
              <ul className="space-y-2">
                <li className="flex items-start gap-2">
                  <span className="w-1.5 h-1.5 rounded-full mt-2 shrink-0 bg-blue-400 dark:bg-blue-500" />
                  <span className="text-blue-700 dark:text-blue-300 leading-relaxed">
                    부작용이 나타나면 즉시 의사 또는 약사에게 알리십시오.
                  </span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="w-1.5 h-1.5 rounded-full mt-2 shrink-0 bg-blue-400 dark:bg-blue-500" />
                  <span className="text-blue-700 dark:text-blue-300 leading-relaxed">
                    약 복용을 임의로 중단하지 마십시오.
                  </span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="w-1.5 h-1.5 rounded-full mt-2 shrink-0 bg-blue-400 dark:bg-blue-500" />
                  <span className="text-blue-700 dark:text-blue-300 leading-relaxed">
                    심각한 부작용이 의심되면 가까운 응급실을 방문하십시오.
                  </span>
                </li>
              </ul>
            </section>
          </>
        ) : (
          /* 부작용 정보 없음 */
          <div className="bg-gray-50 dark:bg-gray-800/50 border border-gray-200 dark:border-gray-700 rounded-xl p-8 text-center mb-8">
            <svg className="w-12 h-12 mx-auto mb-3 text-gray-300 dark:text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
            </svg>
            <p className="text-gray-500 dark:text-gray-400 font-medium">
              부작용 정보가 등록되어 있지 않습니다.
            </p>
            <p className="text-sm text-gray-400 dark:text-gray-500 mt-1">
              자세한 내용은 담당 의사 또는 약사에게 문의하세요.
            </p>
          </div>
        )}

        {/* 네비게이션 링크 */}
        <div className="flex flex-col sm:flex-row gap-3 mb-8">
          <Link
            href={`/drugs/${slug}`}
            className="flex items-center justify-center gap-2 px-4 py-2.5 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl text-sm font-medium text-gray-700 dark:text-gray-300 hover:border-[var(--color-primary-100)] hover:text-[var(--color-primary)] transition-all"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
            </svg>
            {drug.item_name} 상세 정보
          </Link>
          <Link
            href="/drugs/side-effects"
            className="flex items-center justify-center gap-2 px-4 py-2.5 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl text-sm font-medium text-gray-700 dark:text-gray-300 hover:border-[var(--color-primary-100)] hover:text-[var(--color-primary)] transition-all"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
            부작용으로 약물 검색
          </Link>
        </div>

        {/* 광고 */}
        <AdBanner slot="drug-side-effects-bottom" format="horizontal" />

        {/* 면책조항 */}
        <p className="text-xs text-gray-400 dark:text-gray-500 text-center mt-4">
          이 정보는 식약처 공공데이터를 기반으로 하며, 의사/약사의 전문적 판단을 대체하지 않습니다.
        </p>
      </div>
    </>
  );
}
