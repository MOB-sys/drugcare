/** 전문가용 성분 테이블 - 정렬 가능한 밀도 높은 데이터 테이블. */

"use client";

import { useState, useMemo } from "react";
import type { IngredientInfo } from "@/types/drug";

interface ProIngredientsTableProps {
  ingredients: IngredientInfo[];
}

type SortKey = "name" | "amount" | "unit";
type SortDir = "asc" | "desc";

export function ProIngredientsTable({ ingredients }: ProIngredientsTableProps) {
  const [sortKey, setSortKey] = useState<SortKey>("name");
  const [sortDir, setSortDir] = useState<SortDir>("asc");

  const sorted = useMemo(() => {
    return [...ingredients].sort((a, b) => {
      const va = a[sortKey] ?? "";
      const vb = b[sortKey] ?? "";
      const cmp = String(va).localeCompare(String(vb), "ko");
      return sortDir === "asc" ? cmp : -cmp;
    });
  }, [ingredients, sortKey, sortDir]);

  function handleSort(key: SortKey) {
    if (sortKey === key) {
      setSortDir((d) => (d === "asc" ? "desc" : "asc"));
    } else {
      setSortKey(key);
      setSortDir("asc");
    }
  }

  function sortIndicator(key: SortKey) {
    if (sortKey !== key) return "";
    return sortDir === "asc" ? " \u25B2" : " \u25BC";
  }

  const columns: { key: SortKey; label: string }[] = [
    { key: "name", label: "성분명" },
    { key: "amount", label: "함량" },
    { key: "unit", label: "단위" },
  ];

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-xs border-collapse">
        <thead>
          <tr className="bg-gray-100 text-left">
            {columns.map((col) => (
              <th
                key={col.key}
                onClick={() => handleSort(col.key)}
                className="px-3 py-2 font-semibold text-gray-700 cursor-pointer select-none hover:bg-gray-200 border-b border-gray-300"
              >
                {col.label}{sortIndicator(col.key)}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {sorted.map((ing, i) => (
            <tr
              key={i}
              className="border-b border-gray-200 hover:bg-gray-50"
            >
              <td className="px-3 py-1.5 text-gray-900">{ing.name}</td>
              <td className="px-3 py-1.5 text-gray-700 font-mono">
                {ing.amount ?? "-"}
              </td>
              <td className="px-3 py-1.5 text-gray-700">
                {ing.unit ?? "-"}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
