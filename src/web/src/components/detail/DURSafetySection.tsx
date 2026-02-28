/** DUR 안전성 정보 표시 섹션. */

import type { DURSafetyItem } from "@/types/drug";

interface DURSafetySectionProps {
  items: DURSafetyItem[];
}

const DUR_TYPE_CONFIG: Record<string, { label: string; color: string; icon: string }> = {
  pregnancy: { label: "임부금기", color: "text-red-700 bg-red-50 border-red-200", icon: "🤰" },
  elderly: { label: "노인주의", color: "text-orange-700 bg-orange-50 border-orange-200", icon: "👴" },
  dosage: { label: "용량주의", color: "text-amber-700 bg-amber-50 border-amber-200", icon: "💊" },
  duration: { label: "투여기간주의", color: "text-yellow-700 bg-yellow-50 border-yellow-200", icon: "📅" },
  efficacy_dup: { label: "효능군중복", color: "text-purple-700 bg-purple-50 border-purple-200", icon: "🔄" },
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
      <h3 className="text-base font-semibold text-gray-900 mb-3">DUR 안전성 정보</h3>
      <div className="space-y-3">
        {Array.from(grouped.entries()).map(([type, durItems]) => {
          const config = DUR_TYPE_CONFIG[type] || {
            label: durItems[0]?.type_name || type,
            color: "text-gray-700 bg-gray-50 border-gray-200",
            icon: "⚠️",
          };

          return (
            <div key={type} className={`rounded-lg border p-3 ${config.color}`}>
              <p className="font-semibold text-sm mb-1.5">
                {config.icon} {config.label}
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
