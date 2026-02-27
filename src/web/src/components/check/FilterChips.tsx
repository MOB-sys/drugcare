"use client";

import type { SearchFilter } from "@/types/search";

interface FilterChipsProps {
  current: SearchFilter;
  onChange: (filter: SearchFilter) => void;
}

const FILTERS: { value: SearchFilter; label: string }[] = [
  { value: "all", label: "전체" },
  { value: "drug", label: "약물" },
  { value: "supplement", label: "영양제" },
];

export function FilterChips({ current, onChange }: FilterChipsProps) {
  return (
    <div className="flex gap-2" role="group" aria-label="검색 필터">
      {FILTERS.map((f) => (
        <button
          key={f.value}
          onClick={() => onChange(f.value)}
          aria-pressed={current === f.value}
          className={`px-4 py-1.5 rounded-full text-sm font-medium transition-colors ${
            current === f.value
              ? "bg-[var(--color-primary)] text-white shadow-sm"
              : "bg-[var(--color-primary-50)] text-[var(--color-primary)] hover:bg-[var(--color-primary-100)]"
          }`}
        >
          {f.label}
        </button>
      ))}
    </div>
  );
}
