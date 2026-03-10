"use client";

import { useRouter, useSearchParams } from "next/navigation";
import { useState, useEffect, Suspense } from "react";
import { useSearch } from "@/lib/hooks/useSearch";
import { useRecentSearches } from "@/lib/hooks/useRecentSearches";
import { SearchInput } from "@/components/check/SearchInput";
import { FilterChips } from "@/components/check/FilterChips";
import { SearchResults } from "@/components/check/SearchResults";
import { SelectedItemsBar } from "@/components/check/SelectedItemsBar";
import { CheckButton } from "@/components/check/CheckButton";
import { Breadcrumbs } from "@/components/common/Breadcrumbs";

function CheckPageContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const search = useSearch();
  const recent = useRecentSearches();
  const [isChecking, setIsChecking] = useState(false);

  /* URL ?q= 파라미터로 자동 검색 (인기 조합 카드 등에서 유입) */
  useEffect(() => {
    const q = searchParams.get("q");
    if (q) {
      const keywords = q.split(",").filter(Boolean);
      if (keywords.length > 0) {
        search.setQuery(keywords[0]);
      }
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  function handleQueryChange(q: string) {
    search.setQuery(q);
  }

  function handleSearchSelect(q: string) {
    recent.addSearch(q);
  }

  function handleCheck() {
    if (search.selectedItems.length < 2) return;
    setIsChecking(true);
    /* 검색어가 있었으면 최근 검색에 추가 */
    if (search.query.trim()) recent.addSearch(search.query);
    const encoded = search.selectedItems
      .map((i) => `${i.item_type}:${i.item_id}:${encodeURIComponent(i.name)}`)
      .join(",");
    router.push(`/check/result?items=${encoded}`);
  }

  return (
    <>
      <Breadcrumbs
        items={[
          { label: "홈", href: "/" },
          { label: "상호작용 체크" },
        ]}
      />

      <section className="max-w-2xl mx-auto px-4 py-6">
        <h1 className="text-2xl font-bold text-[var(--color-primary)] mb-2">상호작용 체크</h1>
        <p className="text-gray-500 dark:text-gray-400 mb-6">
          복용 중인 약물과 영양제를 검색해서 선택하세요.
        </p>

        <div className="space-y-4">
          <SearchInput
            value={search.query}
            onChange={handleQueryChange}
            recentSearches={recent.recentSearches}
            onSearchSelect={handleSearchSelect}
            onRemoveRecent={recent.removeSearch}
            onClearRecent={recent.clearAll}
          />
          <FilterChips current={search.filter} onChange={search.setFilter} />

          <div className="border border-gray-200 dark:border-gray-700 rounded-xl bg-white dark:bg-gray-800 overflow-hidden shadow-sm">
            <SearchResults
              results={search.results}
              isLoading={search.isLoading}
              query={search.query}
              searchError={search.searchError}
              isSelected={search.isSelected}
              canAddMore={search.canAddMore}
              onToggle={search.toggleItem}
            />
          </div>

          <SelectedItemsBar
            items={search.selectedItems}
            onRemove={search.removeItem}
            onClearAll={search.clearAll}
          />

          <CheckButton
            items={search.selectedItems}
            isLoading={isChecking}
            onClick={handleCheck}
          />
        </div>
      </section>
    </>
  );
}

export default function CheckPage() {
  return (
    <Suspense>
      <CheckPageContent />
    </Suspense>
  );
}
