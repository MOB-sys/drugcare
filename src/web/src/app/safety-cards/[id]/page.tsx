import type { Metadata } from "next";
import Image from "next/image";
import Link from "next/link";
import { notFound } from "next/navigation";
import { Breadcrumbs } from "@/components/common/Breadcrumbs";
import { AdBanner } from "@/components/ads/AdBanner";
import { KakaoShareButton } from "@/components/common/KakaoShareButton";
import { DetailViewTracker } from "@/components/common/DetailViewTracker";
import { SITE_URL } from "@/lib/constants/site";
import indexData from "../data";
import fs from "fs";
import path from "path";

interface PageProps {
  params: Promise<{ id: string }>;
}

interface SceneMeta {
  scene: number;
  name: string;
  image: string;
  narration: string;
  screen_text: string;
  subtitle: string;
}

interface ContentMeta {
  id: string;
  title: string;
  severity: string;
  danger_score: number;
  disclaimer: string;
  source: string;
  scenes: SceneMeta[];
}

function loadMeta(id: string): ContentMeta | null {
  const metaPath = path.join(process.cwd(), "public", "sns-content", id, "meta.json");
  if (!fs.existsSync(metaPath)) return null;
  return JSON.parse(fs.readFileSync(metaPath, "utf-8"));
}

export async function generateStaticParams() {
  return indexData.items.map((item) => ({ id: item.id }));
}

export async function generateMetadata({ params }: PageProps): Promise<Metadata> {
  const { id } = await params;
  const meta = loadMeta(id);
  if (!meta) return { title: "안전 카드" };

  const cleanTitle = meta.title.replace(" — 같이 먹어도 될까?", "");

  return {
    title: `${cleanTitle} 상호작용 안전 카드`,
    description: `${cleanTitle} — 위험도 ${meta.danger_score}/10. ${meta.scenes[1]?.narration || ""} 식약처 DUR 데이터 기반.`,
    keywords: [cleanTitle, "약물 상호작용", "복약 안전", "약잘알"],
    openGraph: {
      title: `${cleanTitle} — 약물 상호작용 안전 카드`,
      description: `위험도 ${meta.danger_score}/10 — ${meta.scenes[1]?.narration || ""}`,
      type: "article",
      url: `${SITE_URL}/safety-cards/${id}`,
      images: [
        {
          url: `${SITE_URL}/sns-content/${id}/01_hook.webp`,
          width: 540,
          height: 960,
          alt: cleanTitle,
        },
      ],
    },
  };
}

const SCENE_LABELS: Record<string, string> = {
  hook: "주의",
  problem: "문제",
  danger: "위험도",
  mechanism: "원인",
  solution: "해결책",
  app_demo: "확인하기",
  cta: "더 알아보기",
};

const SCENE_COLORS: Record<string, string> = {
  hook: "border-red-300 dark:border-red-700",
  problem: "border-purple-300 dark:border-purple-700",
  danger: "border-red-400 dark:border-red-600",
  mechanism: "border-blue-300 dark:border-blue-700",
  solution: "border-green-300 dark:border-green-700",
  app_demo: "border-[var(--color-primary-200)]",
  cta: "border-gray-300 dark:border-gray-600",
};

export default async function SafetyCardDetailPage({ params }: PageProps) {
  const { id } = await params;
  const meta = loadMeta(id);
  if (!meta) notFound();

  const cleanTitle = meta.title.replace(" — 같이 먹어도 될까?", "");
  const severityLabel = meta.severity === "high" ? "높음" : meta.severity === "moderate" ? "보통" : "낮음";
  const severityColor =
    meta.severity === "high"
      ? "text-red-600 dark:text-red-400"
      : meta.severity === "moderate"
        ? "text-yellow-600 dark:text-yellow-400"
        : "text-green-600 dark:text-green-400";

  // 핵심 장면만 표시 (hook, problem, danger, mechanism, solution)
  const displayScenes = meta.scenes.filter((s) =>
    ["hook", "problem", "danger", "mechanism", "solution"].includes(s.name)
  );

  // JSON-LD
  const jsonLd = {
    "@context": "https://schema.org",
    "@type": "Article",
    headline: `${cleanTitle} 상호작용 안전 카드`,
    description: meta.scenes[1]?.narration || "",
    image: `${SITE_URL}/sns-content/${id}/01_hook.webp`,
    publisher: {
      "@type": "Organization",
      name: "약잘알 (PillRight)",
      url: SITE_URL,
    },
  };

  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd).replace(/</g, "\\u003c") }}
      />
      <DetailViewTracker type="drug" id={0} name={`safety-card:${id}`} />

      <Breadcrumbs
        items={[
          { label: "홈", href: "/" },
          { label: "안전 카드", href: "/safety-cards" },
          { label: cleanTitle },
        ]}
      />

      <article className="max-w-2xl mx-auto px-4 py-6">
        {/* 헤더 */}
        <div className="mb-6">
          <h1 className="text-2xl font-bold text-[var(--color-primary)] mb-2">
            {cleanTitle}
          </h1>
          <div className="flex items-center gap-3 text-sm">
            <span className={`font-semibold ${severityColor}`}>
              위험도 {meta.danger_score}/10 · {severityLabel}
            </span>
            <span className="text-gray-400">|</span>
            <span className="text-gray-500 dark:text-gray-400">{meta.source}</span>
          </div>
        </div>

        {/* 카드 캐러셀 — 세로 스크롤 */}
        <div className="space-y-4">
          {displayScenes.map((scene) => (
            <div
              key={scene.scene}
              className={`rounded-xl border-2 ${SCENE_COLORS[scene.name] || "border-gray-200"} overflow-hidden bg-white dark:bg-gray-800`}
            >
              <div className="relative aspect-[9/16] max-h-[480px] mx-auto">
                <Image
                  src={`/sns-content/${id}/${scene.image}`}
                  alt={scene.screen_text}
                  fill
                  sizes="(max-width: 672px) 100vw, 672px"
                  className="object-contain"
                  priority={scene.scene <= 2}
                />
              </div>
              <div className="px-4 py-3 border-t border-gray-100 dark:border-gray-700">
                <span className="inline-block px-2 py-0.5 rounded text-xs font-semibold bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300 mb-1.5">
                  {SCENE_LABELS[scene.name] || scene.name}
                </span>
                <p className="text-sm text-gray-700 dark:text-gray-300 leading-relaxed">
                  {scene.narration}
                </p>
              </div>
            </div>
          ))}
        </div>

        {/* 공유 */}
        <div className="flex gap-2 mt-6">
          <KakaoShareButton
            title={`${cleanTitle} — 상호작용 안전 카드`}
            description={`위험도 ${meta.danger_score}/10. ${meta.scenes[2]?.narration || ""}`}
            buttonLabel="카카오톡 공유"
          />
          <Link
            href="/check"
            className="inline-flex items-center gap-1.5 px-4 py-2.5 rounded-xl text-sm font-semibold text-white bg-[var(--color-primary)] hover:bg-[var(--color-primary-dark)] transition-colors"
          >
            내 약 조합 체크하기
          </Link>
        </div>

        <AdBanner slot="safety-card-detail" format="auto" className="mt-6" />

        {/* 면책조항 */}
        <div className="mt-6 p-4 rounded-xl bg-[var(--color-primary-50)] border border-[var(--color-primary-100)] text-sm text-[var(--color-primary)]">
          <p className="font-medium mb-1">면책조항</p>
          <p className="opacity-80">
            {meta.disclaimer || "이 정보는 참고용이며, 의사/약사의 전문적 판단을 대체하지 않습니다. 반드시 전문가와 상담하세요."}
          </p>
        </div>
      </article>
    </>
  );
}
