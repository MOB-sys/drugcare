"use client";

import { useState, useEffect, useCallback } from "react";
import type { CabinetItem } from "@/types/cabinet";
import {
  getCabinetItems,
  addCabinetItem,
  deleteCabinetItem,
} from "@/lib/api/cabinet";
import { ApiError } from "@/lib/api/client";

interface UseCabinetReturn {
  items: CabinetItem[];
  isLoading: boolean;
  error: string | null;
  addItem: (
    itemType: "drug" | "supplement",
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
      itemType: "drug" | "supplement",
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
    try {
      await deleteCabinetItem(id);
      setItems((prev) => prev.filter((item) => item.id !== id));
      return true;
    } catch {
      return false;
    }
  }, []);

  return { items, isLoading, error, addItem, removeItem, refresh: fetchItems };
}
