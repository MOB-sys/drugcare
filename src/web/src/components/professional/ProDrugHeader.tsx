/** 전문가용 약물 헤더 - 주요 식별 정보를 밀도 높게 표시. */

import type { DrugDetail } from "@/types/drug";

interface ProDrugHeaderProps {
  drug: DrugDetail;
}

const FIELD_ITEMS: { label: string; key: keyof DrugDetail }[] = [
  { label: "제약사", key: "entp_name" },
  { label: "품목기준코드", key: "item_seq" },
  { label: "분류번호", key: "class_no" },
  { label: "전문/일반", key: "etc_otc_code" },
  { label: "표준코드", key: "bar_code" },
  { label: "성상", key: "chart" },
];

export function ProDrugHeader({ drug }: ProDrugHeaderProps) {
  return (
    <div className="border border-gray-300 rounded-lg bg-white overflow-hidden">
      <div className="bg-gray-800 px-4 py-2.5">
        <h1 className="text-lg font-bold text-white leading-tight">
          {drug.item_name}
        </h1>
      </div>
      <div className="grid grid-cols-2 sm:grid-cols-3 text-xs">
        {FIELD_ITEMS.map(({ label, key }) => {
          const value = drug[key];
          if (value === null || value === undefined) return null;
          return (
            <div
              key={key}
              className="border-b border-r border-gray-200 px-3 py-2 last:border-r-0"
            >
              <dt className="text-gray-500 font-medium mb-0.5">{label}</dt>
              <dd className="text-gray-900 break-all">{String(value)}</dd>
            </div>
          );
        })}
      </div>
    </div>
  );
}
