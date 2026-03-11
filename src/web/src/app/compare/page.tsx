"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { searchDrugs } from "@/lib/api/drugs";
import { searchSupplements } from "@/lib/api/supplements";
import { Breadcrumbs } from "@/components/common/Breadcrumbs";
import { AdBanner } from "@/components/ads/AdBanner";
import { useDebounce } from "@/lib/hooks/useDebounce";
import { SITE_URL } from "@/lib/constants/site";
import type { DrugSearchItem, DrugDetail } from "@/types/drug";
import type { SupplementSearchItem, SupplementDetail } from "@/types/supplement";

type CompareItem = {
  type: "drug" | "supplement" | "food" | "herbal";
  id: number;
  name: string;
  sub: string | null;
  slug: string;
  details: Record<string, string | null>;
};

type SearchResult = { type: "drug" | "supplement" | "food" | "herbal"; id: number; name: string; sub: string | null; slug: string };

function DrugSearchBox({
  label,
  selected,
  onSelect,
  onClear,
}: {
  label: string;
  selected: CompareItem | null;
  onSelect: (item: SearchResult) => void;
  onClear: () => void;
}) {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<SearchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const debouncedQuery = useDebounce(query);

  useEffect(() => {
    if (!debouncedQuery.trim()) { setResults([]); return; }
    setLoading(true);
    Promise.all([
      searchDrugs(debouncedQuery, 1, 5).then((r) =>
        r.items.map((d: DrugSearchItem) => ({ type: "drug" as const, id: d.id, name: d.item_name, sub: d.entp_name, slug: d.slug }))
      ).catch(() => []),
      searchSupplements(debouncedQuery, 1, 5).then((r) =>
        r.items.map((s: SupplementSearchItem) => ({ type: "supplement" as const, id: s.id, name: s.product_name, sub: s.company, slug: s.slug }))
      ).catch(() => []),
    ]).then(([drugs, supps]) => {
      setResults([...drugs, ...supps]);
      setLoading(false);
    });
  }, [debouncedQuery]);

  if (selected) {
    return (
      <div className="bg-[var(--color-surface)] rounded-xl border border-[var(--color-border)] p-4">
        <div className="flex items-center justify-between mb-2">
          <span className="text-xs font-semibold text-[var(--color-text-muted)] uppercase">{label}</span>
          <button onClick={onClear} className="text-xs text-[var(--color-text-muted)] hover:text-[var(--color-text-secondary)]">변경</button>
        </div>
        <p className="font-semibold text-[var(--color-text)]">{selected.name}</p>
        {selected.sub && <p className="text-sm text-[var(--color-text-secondary)]">{selected.sub}</p>}
        <span className={`inline-block mt-1 px-2 py-0.5 rounded-md text-xs font-medium ${
          selected.type === "drug" ? "bg-blue-50 text-blue-700" : "bg-emerald-50 text-emerald-700"
        }`}>
          {selected.type === "drug" ? "의약품" : "건강기능식품"}
        </span>
      </div>
    );
  }

  return (
    <div className="bg-[var(--color-surface)] rounded-xl border border-[var(--color-border)] p-4">
      <span className="text-xs font-semibold text-[var(--color-text-muted)] uppercase mb-2 block">{label}</span>
      <input
        type="text"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="약물 또는 영양제 검색..."
        aria-label={`${label} 검색`}
        className="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)] bg-[var(--color-surface)]"
      />
      {loading && <p className="text-xs text-[var(--color-text-muted)] mt-2">검색 중...</p>}
      {results.length > 0 && (
        <ul className="mt-2 space-y-1 max-h-40 overflow-y-auto">
          {results.map((r) => (
            <li key={`${r.type}-${r.id}`}>
              <button
                onClick={() => { onSelect(r); setQuery(""); setResults([]); }}
                className="w-full text-left px-2 py-1.5 rounded-lg hover:bg-[var(--color-surface-hover)] text-sm transition-colors"
              >
                <span className={`inline-block mr-1.5 px-1.5 py-0.5 rounded text-xs ${
                  r.type === "drug" ? "bg-blue-50 text-blue-700" : "bg-emerald-50 text-emerald-700"
                }`}>
                  {r.type === "drug" ? "약" : "영양제"}
                </span>
                <span className="text-[var(--color-text)]">{r.name}</span>
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

const DRUG_FIELDS = [
  { key: "efcy_qesitm", label: "효능·효과" },
  { key: "use_method_qesitm", label: "용법·용량" },
  { key: "atpn_warn_qesitm", label: "주의사항 (경고)" },
  { key: "atpn_qesitm", label: "주의사항" },
  { key: "intrc_qesitm", label: "상호작용" },
  { key: "se_qesitm", label: "부작용" },
  { key: "deposit_method_qesitm", label: "보관방법" },
];

const SUPP_FIELDS = [
  { key: "functionality", label: "기능성" },
  { key: "main_ingredient", label: "주성분" },
  { key: "intake_method", label: "섭취방법" },
  { key: "precautions", label: "섭취 시 주의사항" },
];

export default function ComparePage() {
  const [itemA, setItemA] = useState<CompareItem | null>(null);
  const [itemB, setItemB] = useState<CompareItem | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function loadDetails(item: SearchResult): Promise<CompareItem> {
    if (item.type === "drug") {
      const { getDrugBySlug } = await import("@/lib/api/drugs");
      const d: DrugDetail = await getDrugBySlug(item.slug);
      const details: Record<string, string | null> = {};
      for (const f of DRUG_FIELDS) details[f.key] = d[f.key as keyof DrugDetail] as string | null ?? null;
      details._entp_name = d.entp_name ?? null;
      details._etc_otc_code = d.etc_otc_code ?? null;
      return { ...item, details };
    }
    const { getSupplementBySlug } = await import("@/lib/api/supplements");
    const s: SupplementDetail = await getSupplementBySlug(item.slug);
    const details: Record<string, string | null> = {};
    for (const f of SUPP_FIELDS) details[f.key] = s[f.key as keyof SupplementDetail] as string | null ?? null;
    details._company = s.company ?? null;
    details._category = s.category ?? null;
    return { ...item, details };
  }

  async function handleSelect(slot: "a" | "b", item: SearchResult) {
    setLoading(true);
    setError(null);
    try {
      const detailed = await loadDetails(item);
      if (slot === "a") setItemA(detailed);
      else setItemB(detailed);
    } catch {
      setError("상세 정보를 불러오지 못했습니다. 다시 시도해주세요.");
    }
    setLoading(false);
  }

  const fields = itemA?.type === "supplement" || itemB?.type === "supplement"
    ? [...DRUG_FIELDS, ...SUPP_FIELDS]
    : DRUG_FIELDS;

  const uniqueFields = fields.filter((f, i, arr) => arr.findIndex((x) => x.key === f.key) === i);

  return (
    <>
      <Breadcrumbs
        items={[
          { label: "홈", href: "/" },
          { label: "약물 비교" },
        ]}
      />

      <section className="max-w-4xl mx-auto px-4 py-6">
        <h1 className="text-2xl font-bold text-[var(--color-primary)] mb-2">약물 비교</h1>
        <p className="text-[var(--color-text-secondary)] mb-6">
          두 가지 약물 또는 영양제를 선택해서 나란히 비교해보세요.
        </p>

        {/* 선택 영역 */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-8">
          <DrugSearchBox
            label="약물 A"
            selected={itemA}
            onSelect={(item) => handleSelect("a", item)}
            onClear={() => setItemA(null)}
          />
          <DrugSearchBox
            label="약물 B"
            selected={itemB}
            onSelect={(item) => handleSelect("b", item)}
            onClear={() => setItemB(null)}
          />
        </div>

        {loading && (
          <div className="text-center py-8">
            <div className="inline-block w-6 h-6 border-2 border-[var(--color-primary-100)] border-t-[var(--color-primary)] rounded-full animate-spin" />
            <p className="mt-2 text-sm text-[var(--color-text-muted)]">정보를 불러오는 중...</p>
          </div>
        )}

        {error && (
          <div className="mb-6 p-4 rounded-xl bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 text-sm text-red-700 dark:text-red-300">
            {error}
          </div>
        )}

        {/* 비교 테이블 — PC: 3컬럼 그리드, 모바일: 카드 뷰 */}
        {itemA && itemB && !loading && (
          <>
            {/* PC 테이블 (md 이상) */}
            <div className="hidden md:block bg-[var(--color-surface)] rounded-xl border border-[var(--color-border)] overflow-hidden shadow-sm">
              <div className="grid grid-cols-[140px_1fr_1fr] border-b border-[var(--color-border)] bg-[var(--color-primary-50)]">
                <div className="p-3 text-xs font-semibold text-[var(--color-text-muted)] uppercase">항목</div>
                <div className="p-3 text-sm font-semibold text-[var(--color-primary)] border-l border-[var(--color-border)] truncate">{itemA.name}</div>
                <div className="p-3 text-sm font-semibold text-[var(--color-primary)] border-l border-[var(--color-border)] truncate">{itemB.name}</div>
              </div>
              {uniqueFields.map((field) => {
                const valA = itemA.details[field.key];
                const valB = itemB.details[field.key];
                if (!valA && !valB) return null;
                return (
                  <div key={field.key} className="grid grid-cols-[140px_1fr_1fr] border-b last:border-b-0 border-[var(--color-border-light)]">
                    <div className="p-3 text-sm font-medium text-[var(--color-text-secondary)] bg-[var(--color-surface-hover)]">{field.label}</div>
                    <div className="p-3 text-sm text-[var(--color-text)] leading-relaxed whitespace-pre-line border-l border-[var(--color-border-light)] break-keep">
                      {valA || <span className="text-[var(--color-text-muted)]">—</span>}
                    </div>
                    <div className="p-3 text-sm text-[var(--color-text)] leading-relaxed whitespace-pre-line border-l border-[var(--color-border-light)] break-keep">
                      {valB || <span className="text-[var(--color-text-muted)]">—</span>}
                    </div>
                  </div>
                );
              })}
            </div>

            {/* 모바일 카드 뷰 (md 미만) */}
            <div className="md:hidden space-y-4">
              {uniqueFields.map((field) => {
                const valA = itemA.details[field.key];
                const valB = itemB.details[field.key];
                if (!valA && !valB) return null;
                return (
                  <div key={field.key} className="bg-[var(--color-surface)] rounded-xl border border-[var(--color-border)] overflow-hidden shadow-sm">
                    <div className="px-4 py-2 bg-[var(--color-primary-50)] text-sm font-semibold text-[var(--color-primary)]">
                      {field.label}
                    </div>
                    <div className="divide-y divide-[var(--color-border-light)]">
                      <div className="px-4 py-3">
                        <p className="text-xs font-medium text-[var(--color-text-muted)] mb-1">{itemA.name}</p>
                        <p className="text-sm text-[var(--color-text)] leading-relaxed whitespace-pre-line break-keep">
                          {valA || <span className="text-[var(--color-text-muted)]">—</span>}
                        </p>
                      </div>
                      <div className="px-4 py-3">
                        <p className="text-xs font-medium text-[var(--color-text-muted)] mb-1">{itemB.name}</p>
                        <p className="text-sm text-[var(--color-text)] leading-relaxed whitespace-pre-line break-keep">
                          {valB || <span className="text-[var(--color-text-muted)]">—</span>}
                        </p>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </>
        )}

        {/* 상호작용 체크 유도 */}
        {itemA && itemB && !loading && (
          <div className="mt-6 text-center">
            <Link
              href={`/check?preselect=${itemA.type}:${itemA.id}:${encodeURIComponent(itemA.name)},${itemB.type}:${itemB.id}:${encodeURIComponent(itemB.name)}`}
              className="inline-block px-6 py-3 rounded-xl text-white font-semibold bg-[var(--color-primary)] hover:bg-[var(--color-primary-dark)] shadow-md transition-all active:scale-[0.98]"
            >
              이 두 약의 상호작용 체크하기
            </Link>
          </div>
        )}

        {/* 비교 결과 하단 광고 */}
        <AdBanner slot="compare-mid" format="auto" className="max-w-4xl mx-auto" />

        {!itemA && !itemB && (
          <div className="text-center py-12 text-[var(--color-text-muted)]">
            <svg className="w-12 h-12 mx-auto mb-3 text-[var(--color-primary-100)]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
            </svg>
            <p className="text-sm">위에서 비교할 약물 두 개를 선택해주세요</p>
          </div>
        )}
      </section>
    </>
  );
}
