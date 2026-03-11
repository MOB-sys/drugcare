/** DUR 안전성 정보 표시 섹션. */

import React from "react";
import type { DURSafetyItem } from "@/types/drug";

interface DURSafetySectionProps {
  items: DURSafetyItem[];
}

function PregnancyIcon() {
  return (
    <svg className="w-4 h-4 inline-block mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z" />
    </svg>
  );
}

function ElderlyIcon() {
  return (
    <svg className="w-4 h-4 inline-block mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
    </svg>
  );
}

function DosageIcon() {
  return (
    <svg className="w-4 h-4 inline-block mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" />
    </svg>
  );
}

function DurationIcon() {
  return (
    <svg className="w-4 h-4 inline-block mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
    </svg>
  );
}

function DuplicateIcon() {
  return (
    <svg className="w-4 h-4 inline-block mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
    </svg>
  );
}

function WarningIcon() {
  return (
    <svg className="w-4 h-4 inline-block mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z" />
    </svg>
  );
}

const DUR_TYPE_CONFIG: Record<string, { label: string; color: string; Icon: React.FC }> = {
  pregnancy: { label: "임부금기", color: "text-red-700 bg-red-50 border-red-200", Icon: PregnancyIcon },
  elderly: { label: "노인주의", color: "text-orange-700 bg-orange-50 border-orange-200", Icon: ElderlyIcon },
  dosage: { label: "용량주의", color: "text-amber-700 bg-amber-50 border-amber-200", Icon: DosageIcon },
  duration: { label: "투여기간주의", color: "text-yellow-700 bg-yellow-50 border-yellow-200", Icon: DurationIcon },
  efficacy_dup: { label: "효능군중복", color: "text-purple-700 bg-purple-50 border-purple-200", Icon: DuplicateIcon },
};

function groupByType(items: DURSafetyItem[]): Map<string, DURSafetyItem[]> {
  const map = new Map<string, DURSafetyItem[]>();
  for (const item of items) {
    const key = item.dur_type;
    if (!map.has(key)) map.set(key, []);
    map.get(key)!.push(item);
  }
  return map;
}

export function DURSafetySection({ items }: DURSafetySectionProps) {
  if (!items.length) return null;

  const grouped = groupByType(items);

  return (
    <div id="dur-safety" className="py-5 scroll-mt-24">
      <h3 className="text-base font-semibold text-gray-900 dark:text-white mb-3">DUR 안전성 정보</h3>
      <div className="space-y-3">
        {Array.from(grouped.entries()).map(([type, durItems]) => {
          const config = DUR_TYPE_CONFIG[type] || {
            label: durItems[0]?.type_name || type,
            color: "text-gray-700 dark:text-gray-200 bg-gray-50 dark:bg-gray-800 border-gray-200 dark:border-gray-700",
            Icon: WarningIcon,
          };

          return (
            <div key={type} className={`rounded-lg border p-3 ${config.color}`}>
              <p className="font-semibold text-sm mb-1.5 flex items-center">
                <config.Icon /> {config.label}
              </p>
              <ul className="space-y-1.5">
                {durItems.map((item, idx) => (
                  <li key={idx} className="text-sm leading-relaxed">
                    {item.ingr_name && (
                      <span className="font-medium">[{item.ingr_name}] </span>
                    )}
                    {item.prohibition_content || "상세 정보를 확인하세요."}
                    {item.remark && (
                      <span className="block text-xs mt-0.5 opacity-75">{item.remark}</span>
                    )}
                  </li>
                ))}
              </ul>
            </div>
          );
        })}
      </div>
    </div>
  );
}
