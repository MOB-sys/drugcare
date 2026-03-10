"use client";

import { useCabinet } from "@/lib/hooks/useCabinet";
import { CabinetItemCard } from "@/components/cabinet/CabinetItemCard";
import { EmptyState } from "@/components/cabinet/EmptyState";
import { AdBanner } from "@/components/ads/AdBanner";
import { Breadcrumbs } from "@/components/common/Breadcrumbs";
import Link from "next/link";

export default function CabinetPage() {
  const { items, isLoading, error, deletingIds, removeItem } = useCabinet();

  const checkParams = items
    .map((it) => `${it.item_type}:${it.item_id}:${encodeURIComponent(it.nickname || it.item_name)}`)
    .join(",");

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

        <p className="text-xs text-gray-400 dark:text-gray-500 text-center mt-6">
          이 서비스는 의사/약사의 전문적 판단을 대체하지 않습니다.
        </p>
      </div>
    </>
  );
}
