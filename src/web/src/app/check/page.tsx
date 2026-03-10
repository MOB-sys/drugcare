"use client";

import { useRouter, useSearchParams } from "next/navigation";
import { useState, useEffect, useRef, Suspense } from "react";
import { useSearch } from "@/lib/hooks/useSearch";
import { useRecentSearches } from "@/lib/hooks/useRecentSearches";
import { searchDrugs } from "@/lib/api/drugs";
import { searchSupplements } from "@/lib/api/supplements";
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
  const autoSelectApplied = useRef(false);

  /* URL ?q= 파라미터로 자동 검색 + 자동 선택 (인기 조합 카드 등에서 유입) */
  useEffect(() => {
    if (autoSelectApplied.current) return;
    const q = searchParams.get("q");
    if (!q) return;
    autoSelectApplied.current = true;

    const keywords = q.split(",").map((k) => k.trim()).filter(Boolean);
    if (keywords.length === 0) return;

    // 각 키워드를 검색하여 첫 번째 결과를 자동 선택
    async function autoSelect() {
      for (const keyword of keywords) {
        try {
          const [drugRes, suppRes] = await Promise.all([
            searchDrugs(keyword, 1, 1).catch(() => ({ items: [] })),
            searchSupplements(keyword, 1, 1).catch(() => ({ items: [] })),
          ]);
          const drug = drugRes.items[0];
          const supp = suppRes.items[0];
          // 약물 이름이 정확히 일치하면 약물 우선, 아니면 영양제
          const match = drug
            ? { item_type: "drug" as const, item_id: drug.id, name: drug.item_name }
            : supp
              ? { item_type: "supplement" as const, item_id: supp.id, name: supp.product_name }
              : null;
          if (match) {
            search.toggleItem(match);
          }
        } catch { /* 개별 키워드 실패 무시 */ }
      }
    }

    autoSelect();
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
