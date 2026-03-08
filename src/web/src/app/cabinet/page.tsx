"use client";

import { useCabinet } from "@/lib/hooks/useCabinet";
import { CabinetItemCard } from "@/components/cabinet/CabinetItemCard";
import { EmptyState } from "@/components/cabinet/EmptyState";
import { AdBanner } from "@/components/ads/AdBanner";
import { Breadcrumbs } from "@/components/common/Breadcrumbs";
import { getStoreUrlForPlatform } from "@/lib/constants/appStore";
import Link from "next/link";

export default function CabinetPage() {
  const { items, isLoading, error, deletingIds, removeItem } = useCabinet();

  const checkParams = items
    .map((it) => `${it.item_type}:${it.item_id}:${encodeURIComponent(it.nickname || it.item_name)}`)
    .join(",");

  const storeUrl = getStoreUrlForPlatform("cabinet-cta");

  return (
    <>
      <Breadcrumbs
        items={[
          { label: "홈", href: "/" },
          { label: "내 복약함" },
        ]}
      />

      <div className="max-w-2xl mx-auto px-4 py-6">
        <h1 className="text-2xl font-bold text-[var(--color-primary)] mb-6">내 복약함</h1>

        {isLoading && (
          <div className="text-center py-16 text-gray-400">불러오는 중...</div>
        )}

        {error && (
          <div className="text-center py-16">
            <p className="text-red-500 mb-2">{error}</p>
            <p className="text-sm text-gray-400">
              새로고침하거나 나중에 다시 시도해주세요.
            </p>
          </div>
        )}

        {!isLoading && !error && items.length === 0 && <EmptyState />}

        {!isLoading && !error && items.length > 0 && (
          <>
            <div className="space-y-2 mb-6">
              {items.map((item) => (
                <CabinetItemCard
                  key={item.id}
                  item={item}
                  isDeleting={deletingIds.has(item.id)}
                  onDelete={removeItem}
                />
              ))}
            </div>

            {items.length >= 2 && (
              <Link
                href={`/check?preselect=${checkParams}`}
                className="block w-full py-3 rounded-xl text-center text-white font-semibold bg-[var(--color-primary)] hover:bg-[var(--color-primary-dark)] shadow-md transition-all"
              >
                전체 상호작용 확인하기 ({items.length}개)
              </Link>
            )}
          </>
        )}

        <AdBanner slot="cabinet-bottom" format="horizontal" className="mt-8" />

        {/* 앱 유도 */}
        <div className="mt-8 p-4 rounded-xl bg-[var(--color-primary-50)] border border-[var(--color-primary-100)] text-center">
          <p className="text-sm font-medium text-[var(--color-primary)] mb-1">
            매일 복약 리마인더가 필요하다면?
          </p>
          <p className="text-xs text-gray-500 mb-3">
            PillRight 앱에서 푸시 알림으로 복용 시간을 놓치지 마세요.
          </p>
          <a
            href={storeUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-block px-5 py-2 rounded-xl text-white text-sm font-semibold bg-[var(--color-primary)] hover:bg-[var(--color-primary-dark)] shadow-md transition-all"
          >
            앱 다운로드
          </a>
        </div>

        <p className="text-xs text-gray-400 text-center mt-6">
          이 서비스는 의사/약사의 전문적 판단을 대체하지 않습니다.
        </p>
      </div>
    </>
  );
}
