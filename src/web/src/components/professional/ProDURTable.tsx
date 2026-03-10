/** 전문가용 DUR 안전성 테이블 - 정렬 가능, 심각도 색상 구분. */

"use client";

import { useState, useMemo } from "react";
import type { DURSafetyItem } from "@/types/drug";

interface ProDURTableProps {
  items: DURSafetyItem[];
}

type SortKey = "dur_type" | "ingr_name" | "prohibition_content" | "remark";
type SortDir = "asc" | "desc";

const SEVERITY_COLORS: Record<string, string> = {
  pregnancy: "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200",
  elderly: "bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200",
  dosage: "bg-amber-100 text-amber-800 dark:bg-amber-900 dark:text-amber-200",
  duration: "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200",
  efficacy_dup: "bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200",
};

const TYPE_LABELS: Record<string, string> = {
  pregnancy: "임부금기",
  elderly: "노인주의",
  dosage: "용량주의",
  duration: "투여기간주의",
  efficacy_dup: "효능군중복",
};

export function ProDURTable({ items }: ProDURTableProps) {
  const [sortKey, setSortKey] = useState<SortKey>("dur_type");
  const [sortDir, setSortDir] = useState<SortDir>("asc");

  const sorted = useMemo(() => {
    return [...items].sort((a, b) => {
      const va = a[sortKey] ?? "";
      const vb = b[sortKey] ?? "";
      const cmp = String(va).localeCompare(String(vb), "ko");
      return sortDir === "asc" ? cmp : -cmp;
    });
  }, [items, sortKey, sortDir]);

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
    { key: "dur_type", label: "DUR 유형" },
    { key: "ingr_name", label: "관련 성분" },
    { key: "prohibition_content", label: "금기 내용" },
    { key: "remark", label: "비고" },
  ];

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-xs border-collapse">
        <thead>
          <tr className="bg-gray-100 dark:bg-gray-800 text-left">
            {columns.map((col) => (
              <th
                key={col.key}
                className="px-3 py-2 font-semibold text-gray-700 dark:text-gray-300 border-b border-gray-300 dark:border-gray-700 whitespace-nowrap"
              >
                <button
                  type="button"
                  onClick={() => handleSort(col.key)}
                  aria-label={`${col.label} 기준으로 정렬`}
                  className="w-full text-left cursor-pointer select-none hover:text-gray-900 dark:hover:text-gray-100 transition-colors"
                >
                  {col.label}{sortIndicator(col.key)}
                </button>
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {sorted.map((item, i) => {
            const colorCls =
              SEVERITY_COLORS[item.dur_type] ?? "bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200";
            const typeLabel =
              TYPE_LABELS[item.dur_type] ??
              item.type_name ??
              item.dur_type;
            return (
              <tr
                key={i}
                className="border-b border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-800"
              >
                <td className="px-3 py-1.5">
                  <span
                    className={`inline-block px-1.5 py-0.5 rounded text-[10px] font-semibold ${colorCls}`}
                  >
                    {typeLabel}
                  </span>
                </td>
                <td className="px-3 py-1.5 text-gray-900 dark:text-gray-100 font-medium">
                  {item.ingr_name ?? "-"}
                </td>
                <td className="px-3 py-1.5 text-gray-700 dark:text-gray-300 max-w-md">
                  {item.prohibition_content ?? "-"}
                </td>
                <td className="px-3 py-1.5 text-gray-500 dark:text-gray-400">
                  {item.remark ?? "-"}
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
