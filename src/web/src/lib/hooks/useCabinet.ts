"use client";

import { useState, useEffect, useCallback } from "react";
import type { CabinetItem } from "@/types/cabinet";
import {
  getCabinetItems,
  addCabinetItem,
  deleteCabinetItem,
} from "@/lib/api/cabinet";
import { ApiError } from "@/lib/api/client";
import { track } from "@/lib/analytics/track";

interface UseCabinetReturn {
  items: CabinetItem[];
  isLoading: boolean;
  error: string | null;
  deletingIds: Set<number>;
  addItem: (
    itemType: "drug" | "supplement" | "food" | "herbal",
    itemId: number,
    itemName: string,
  ) => Promise<{ success: boolean; duplicate?: boolean }>;
  removeItem: (id: number) => Promise<boolean>;
  refresh: () => Promise<void>;
}

export function useCabinet(): UseCabinetReturn {
  const [items, setItems] = useState<CabinetItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [deletingIds, setDeletingIds] = useState<Set<number>>(new Set());

  const fetchItems = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await getCabinetItems();
      setItems(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : "복약함을 불러올 수 없습니다.");
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchItems();
  }, [fetchItems]);

  const addItem = useCallback(
    async (
      itemType: "drug" | "supplement" | "food" | "herbal",
      itemId: number,
      itemName: string,
    ): Promise<{ success: boolean; duplicate?: boolean }> => {
      try {
        const newItem = await addCabinetItem({
          item_type: itemType,
          item_id: itemId,
          nickname: itemName,
        });
        setItems((prev) => [...prev, newItem]);
        track("cabinet_add", { type: itemType, id: itemId, name: itemName });
        return { success: true };
      } catch (e) {
        if (e instanceof ApiError && e.status === 409) {
          return { success: false, duplicate: true };
        }
        return { success: false };
      }
    },
    [],
  );

  const removeItem = useCallback(async (id: number): Promise<boolean> => {
    setDeletingIds((prev) => new Set(prev).add(id));
    try {
      await deleteCabinetItem(id);
      setItems((prev) => prev.filter((item) => item.id !== id));
      track("cabinet_remove", { id });
      return true;
    } catch (e) {
      console.error("[useCabinet] 복약함 항목 삭제 실패:", e);
      return false;
    } finally {
      setDeletingIds((prev) => {
        const next = new Set(prev);
        next.delete(id);
        return next;
      });
    }
  }, []);

  return { items, isLoading, error, deletingIds, addItem, removeItem, refresh: fetchItems };
}
