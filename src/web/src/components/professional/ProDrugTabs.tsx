/** 전문가용 약물 상세 탭 인터페이스. */

"use client";

import { useState } from "react";
import type { DrugDetail } from "@/types/drug";
import { ProIngredientsTable } from "./ProIngredientsTable";
import { ProDURTable } from "./ProDURTable";

interface ProDrugTabsProps {
  drug: DrugDetail;
}

interface TabDef {
  id: string;
  label: string;
  available: boolean;
}

export function ProDrugTabs({ drug }: ProDrugTabsProps) {
  const tabs: TabDef[] = buildTabs(drug);
  const [activeTab, setActiveTab] = useState(tabs[0]?.id ?? "pharmacology");

  return (
    <div className="border border-gray-300 rounded-lg bg-white overflow-hidden">
      {/* Tab bar */}
      <div className="flex overflow-x-auto border-b border-gray-300 bg-gray-50">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`px-4 py-2.5 text-xs font-semibold whitespace-nowrap border-b-2 transition-colors ${
              activeTab === tab.id
                ? "border-gray-800 text-gray-900 bg-white"
                : "border-transparent text-gray-500 hover:text-gray-700 hover:bg-gray-100"
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Tab content */}
      <div className="p-4">
        {activeTab === "pharmacology" && (
          <PharmacologyTab drug={drug} />
        )}
        {activeTab === "dosage" && (
          <TextBlock content={drug.use_method_qesitm} />
        )}
        {activeTab === "warnings" && (
          <WarningsTab drug={drug} />
        )}
        {activeTab === "interactions" && (
          <TextBlock content={drug.intrc_qesitm} />
        )}
        {activeTab === "sideEffects" && (
          <TextBlock content={drug.se_qesitm} />
        )}
        {activeTab === "durSafety" && drug.dur_safety && (
          <ProDURTable items={drug.dur_safety} />
        )}
        {activeTab === "storage" && (
          <TextBlock content={drug.deposit_method_qesitm} />
        )}
      </div>
    </div>
  );
}

/** 탭 목록 생성 - 데이터가 있는 탭만 포함. */
function buildTabs(drug: DrugDetail): TabDef[] {
  const all: TabDef[] = [
    { id: "pharmacology", label: "약리정보", available: !!(drug.efcy_qesitm || drug.ingredients?.length) },
    { id: "dosage", label: "용법/용량", available: !!drug.use_method_qesitm },
    { id: "warnings", label: "주의사항", available: !!(drug.atpn_warn_qesitm || drug.atpn_qesitm) },
    { id: "interactions", label: "상호작용", available: !!drug.intrc_qesitm },
    { id: "sideEffects", label: "부작용", available: !!drug.se_qesitm },
    { id: "durSafety", label: "DUR 안전성", available: !!(drug.dur_safety?.length) },
    { id: "storage", label: "보관", available: !!drug.deposit_method_qesitm },
  ];
  return all.filter((t) => t.available);
}

/** 약리정보 탭 - 효능 + 성분 테이블. */
function PharmacologyTab({ drug }: { drug: DrugDetail }) {
  return (
    <div className="space-y-4">
      {drug.efcy_qesitm && (
        <div>
          <h4 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">
            효능/효과
          </h4>
          <p className="text-xs text-gray-800 leading-relaxed whitespace-pre-line">
            {drug.efcy_qesitm}
          </p>
        </div>
      )}
      {drug.ingredients && drug.ingredients.length > 0 && (
        <div>
          <h4 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">
            성분 ({drug.ingredients.length}건)
          </h4>
          <ProIngredientsTable ingredients={drug.ingredients} />
        </div>
      )}
    </div>
  );
}

/** 주의사항 탭 - 경고 + 일반 주의. */
function WarningsTab({ drug }: { drug: DrugDetail }) {
  return (
    <div className="space-y-4">
      {drug.atpn_warn_qesitm && (
        <div>
          <h4 className="text-xs font-semibold text-red-600 uppercase tracking-wider mb-1">
            경고
          </h4>
          <p className="text-xs text-gray-800 leading-relaxed whitespace-pre-line bg-red-50 border border-red-200 rounded p-3">
            {drug.atpn_warn_qesitm}
          </p>
        </div>
      )}
      {drug.atpn_qesitm && (
        <div>
          <h4 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">
            일반 주의사항
          </h4>
          <p className="text-xs text-gray-800 leading-relaxed whitespace-pre-line">
            {drug.atpn_qesitm}
          </p>
        </div>
      )}
    </div>
  );
}

/** 단순 텍스트 블록. */
function TextBlock({ content }: { content: string | null }) {
  if (!content) return <p className="text-xs text-gray-400">정보 없음</p>;
  return (
    <p className="text-xs text-gray-800 leading-relaxed whitespace-pre-line">
      {content}
    </p>
  );
}
