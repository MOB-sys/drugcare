/** 상호작용 확인 CTA 버튼. */

import Link from "next/link";

interface CheckCTAProps {
  itemType: "drug" | "supplement";
  itemId: number;
  itemName: string;
}

export function CheckCTA({ itemType, itemId, itemName }: CheckCTAProps) {
  const encoded = `${itemType}:${itemId}:${encodeURIComponent(itemName)}`;
  return (
    <div className="py-6">
      <Link
        href={`/check?preselect=${encoded}`}
        className="block w-full py-3 rounded-xl text-center text-white font-semibold bg-[var(--color-primary)] hover:bg-[var(--color-primary-dark)] shadow-md hover:shadow-lg active:scale-[0.98] transition-all"
      >
        이 {itemType === "drug" ? "약" : "영양제"}의 상호작용 확인하기
      </Link>
    </div>
  );
}
