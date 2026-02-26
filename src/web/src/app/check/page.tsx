"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { useSearch } from "@/lib/hooks/useSearch";
import { SearchInput } from "@/components/check/SearchInput";
import { FilterChips } from "@/components/check/FilterChips";
import { SearchResults } from "@/components/check/SearchResults";
import { SelectedItemsBar } from "@/components/check/SelectedItemsBar";
import { CheckButton } from "@/components/check/CheckButton";

export default function CheckPage() {
  const router = useRouter();
  const search = useSearch();
  const [isChecking, setIsChecking] = useState(false);

  function handleCheck() {
    if (search.selectedItems.length < 2) return;
    setIsChecking(true);
    const encoded = search.selectedItems
      .map((i) => `${i.item_type}:${i.item_id}:${encodeURIComponent(i.name)}`)
      .join(",");
    router.push(`/check/result?items=${encoded}`);
  }

  return (
    <section className="max-w-2xl mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold text-gray-900 mb-2">상호작용 체크</h1>
      <p className="text-gray-500 mb-6">
        복용 중인 약물과 영양제를 검색해서 선택하세요.
      </p>

      <div className="space-y-4">
        <SearchInput value={search.query} onChange={search.setQuery} />
        <FilterChips current={search.filter} onChange={search.setFilter} />

        <div className="border border-gray-200 rounded-lg bg-white overflow-hidden">
          <SearchResults
            results={search.results}
            isLoading={search.isLoading}
            query={search.query}
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
  );
}
