/** 검색 + 아이템 선택 훅. */

"use client";

import { useState, useEffect, useCallback, useRef } from "react";
import { useDebounce } from "./useDebounce";
import { searchDrugs } from "@/lib/api/drugs";
import { searchSupplements } from "@/lib/api/supplements";
import type { DrugSearchItem } from "@/types/drug";
import type { SupplementSearchItem } from "@/types/supplement";
import type { SearchFilter, SelectedItem } from "@/types/search";
import { MAX_INTERACTION_ITEMS } from "@/lib/constants/severity";

export interface SearchResultItem {
  item_type: "drug" | "supplement";
  item_id: number;
  name: string;
  sub: string | null;
}

export interface UseSearchReturn {
  query: string;
  setQuery: (q: string) => void;
  filter: SearchFilter;
  setFilter: (f: SearchFilter) => void;
  results: SearchResultItem[];
  isLoading: boolean;
  searchError: string | null;
  selectedItems: SelectedItem[];
  toggleItem: (item: SelectedItem) => void;
  removeItem: (item_id: number, item_type: string) => void;
  clearAll: () => void;
  isSelected: (item_id: number, item_type: string) => boolean;
  canAddMore: boolean;
}

function toDrugResult(d: DrugSearchItem): SearchResultItem {
  return { item_type: "drug", item_id: d.id, name: d.item_name, sub: d.entp_name };
}

function toSupplementResult(s: SupplementSearchItem): SearchResultItem {
  return { item_type: "supplement", item_id: s.id, name: s.product_name, sub: s.company };
}

function parsePreselect(param: string | null): SelectedItem[] {
  if (!param) return [];
  try {
    return param.split(",").reduce<SelectedItem[]>((acc, part) => {
      const [type, id, ...nameParts] = part.split(":");
      if ((type === "drug" || type === "supplement") && id && nameParts.length) {
        acc.push({
          item_type: type,
          item_id: Number(id),
          name: decodeURIComponent(nameParts.join(":")),
        });
      }
      return acc;
    }, []);
  } catch {
    return [];
  }
}

export function useSearch(): UseSearchReturn {
  const [query, setQuery] = useState("");
  const [filter, setFilter] = useState<SearchFilter>("all");
  const [results, setResults] = useState<SearchResultItem[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [searchError, setSearchError] = useState<string | null>(null);
  const [selectedItems, setSelectedItems] = useState<SelectedItem[]>([]);
  const abortRef = useRef<AbortController | null>(null);
  const preselectApplied = useRef(false);
  const requestIdRef = useRef(0);

  /* URL ?preselect= 파라미터에서 초기 선택 아이템 복원 */
  useEffect(() => {
    if (preselectApplied.current) return;
    preselectApplied.current = true;
    const params = new URLSearchParams(window.location.search);
    const items = parsePreselect(params.get("preselect"));
    if (items.length > 0) {
      setSelectedItems(items);
    }
  }, []);

  const debouncedQuery = useDebounce(query);

  const isSelected = useCallback(
    (item_id: number, item_type: string) =>
      selectedItems.some((s) => s.item_id === item_id && s.item_type === item_type),
    [selectedItems],
  );

  const canAddMore = selectedItems.length < MAX_INTERACTION_ITEMS;

  const toggleItem = useCallback(
    (item: SelectedItem) => {
      setSelectedItems((prev) => {
        const exists = prev.some(
          (s) => s.item_id === item.item_id && s.item_type === item.item_type,
        );
        if (exists) return prev.filter((s) => !(s.item_id === item.item_id && s.item_type === item.item_type));
        if (prev.length >= MAX_INTERACTION_ITEMS) return prev;
        return [...prev, item];
      });
    },
    [],
  );

  const removeItem = useCallback((item_id: number, item_type: string) => {
    setSelectedItems((prev) =>
      prev.filter((s) => !(s.item_id === item_id && s.item_type === item_type)),
    );
  }, []);

  const clearAll = useCallback(() => setSelectedItems([]), []);

  useEffect(() => {
    if (!debouncedQuery.trim()) {
      setResults([]);
      setSearchError(null);
      return;
    }

    abortRef.current?.abort();
    const controller = new AbortController();
    abortRef.current = controller;
    const currentRequestId = ++requestIdRef.current;

    async function doSearch() {
      setIsLoading(true);
      setSearchError(null);
      try {
        const merged: SearchResultItem[] = [];

        if (filter === "all" || filter === "drug") {
          const drugs = await searchDrugs(debouncedQuery, 1, 10);
          merged.push(...drugs.items.map(toDrugResult));
        }
        if (filter === "all" || filter === "supplement") {
          const supps = await searchSupplements(debouncedQuery, 1, 10);
          merged.push(...supps.items.map(toSupplementResult));
        }

        if (!controller.signal.aborted && currentRequestId === requestIdRef.current) {
          setResults(merged);
        }
      } catch (error) {
        if (!controller.signal.aborted && currentRequestId === requestIdRef.current) {
          setResults([]);
          const message =
            error instanceof Error && error.message.includes("시간이 초과")
              ? "요청 시간이 초과되었습니다. 다시 시도해주세요."
              : "검색 중 오류가 발생했습니다. 다시 시도해주세요.";
          setSearchError(message);
        }
      } finally {
        if (!controller.signal.aborted && currentRequestId === requestIdRef.current) {
          setIsLoading(false);
        }
      }
    }

    doSearch();
    return () => controller.abort();
  }, [debouncedQuery, filter]);

  return {
    query,
    setQuery,
    filter,
    setFilter,
    results,
    isLoading,
    searchError,
    selectedItems,
    toggleItem,
    removeItem,
    clearAll,
    isSelected,
    canAddMore,
  };
}
