/** 전문가용 약물 검색 입력 컴포넌트. */

"use client";

import { useState, useCallback } from "react";
import { useRouter } from "next/navigation";

export function ProSearch() {
  const [query, setQuery] = useState("");
  const router = useRouter();

  const handleSubmit = useCallback(
    (e: React.FormEvent) => {
      e.preventDefault();
      const trimmed = query.trim();
      if (!trimmed) return;
      router.push(`/drugs?q=${encodeURIComponent(trimmed)}`);
    },
    [query, router],
  );

  return (
    <form onSubmit={handleSubmit} className="flex gap-2">
      <input
        type="text"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="약물명 또는 성분명으로 검색..."
        className="flex-1 px-3 py-2 text-sm border border-gray-300 rounded-md bg-white text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-1 focus:ring-gray-400 focus:border-gray-400"
      />
      <button
        type="submit"
        className="px-4 py-2 text-sm font-medium text-white bg-gray-800 rounded-md hover:bg-gray-700 transition-colors"
      >
        검색
      </button>
    </form>
  );
}
