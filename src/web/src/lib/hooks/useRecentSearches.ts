"use client";

import { useState, useCallback, useEffect } from "react";

const STORAGE_KEY = "pillright_recent_searches";
const MAX_RECENT = 8;

export function useRecentSearches() {
  const [recentSearches, setRecentSearches] = useState<string[]>([]);

  useEffect(() => {
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      if (stored) setRecentSearches(JSON.parse(stored));
    } catch (e) { console.error("[useRecentSearches] localStorage 읽기 실패:", e); }
  }, []);

  const addSearch = useCallback((query: string) => {
    const trimmed = query.trim();
    if (!trimmed) return;
    setRecentSearches((prev) => {
      const filtered = prev.filter((s) => s !== trimmed);
      const updated = [trimmed, ...filtered].slice(0, MAX_RECENT);
      try { localStorage.setItem(STORAGE_KEY, JSON.stringify(updated)); } catch (e) { console.error("[useRecentSearches] localStorage 저장 실패:", e); }
      return updated;
    });
  }, []);

  const removeSearch = useCallback((query: string) => {
    setRecentSearches((prev) => {
      const updated = prev.filter((s) => s !== query);
      try { localStorage.setItem(STORAGE_KEY, JSON.stringify(updated)); } catch (e) { console.error("[useRecentSearches] localStorage 저장 실패:", e); }
      return updated;
    });
  }, []);

  const clearAll = useCallback(() => {
    setRecentSearches([]);
    try { localStorage.removeItem(STORAGE_KEY); } catch (e) { console.error("[useRecentSearches] localStorage 삭제 실패:", e); }
  }, []);

  return { recentSearches, addSearch, removeSearch, clearAll };
}
