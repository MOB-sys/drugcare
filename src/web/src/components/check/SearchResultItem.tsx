"use client";

interface SearchResultItemProps {
  name: string;
  sub: string | null;
  itemType: "drug" | "supplement";
  selected: boolean;
  disabled: boolean;
  onToggle: () => void;
}

export function SearchResultItem({
  name,
  sub,
  itemType,
  selected,
  disabled,
  onToggle,
}: SearchResultItemProps) {
  return (
    <button
      onClick={onToggle}
      disabled={disabled && !selected}
      className={`w-full text-left px-4 py-3 flex items-center gap-3 transition-colors ${
        selected
          ? "bg-teal-50 border-l-4 border-[var(--color-brand)]"
          : disabled
            ? "opacity-50 cursor-not-allowed"
            : "hover:bg-gray-50"
      }`}
    >
      <span
        className={`shrink-0 px-2 py-0.5 rounded text-xs font-medium ${
          itemType === "drug"
            ? "bg-blue-100 text-blue-700"
            : "bg-green-100 text-green-700"
        }`}
      >
        {itemType === "drug" ? "약물" : "영양제"}
      </span>
      <div className="min-w-0 flex-1">
        <p className="font-medium text-gray-900 truncate">{name}</p>
        {sub && <p className="text-sm text-gray-500 truncate">{sub}</p>}
      </div>
      {selected && (
        <svg className="w-5 h-5 text-[var(--color-brand)] shrink-0" fill="currentColor" viewBox="0 0 20 20">
          <path
            fillRule="evenodd"
            d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
            clipRule="evenodd"
          />
        </svg>
      )}
    </button>
  );
}
