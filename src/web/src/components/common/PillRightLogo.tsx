/** 약잘알 brand logo — shield + check SVG symbol with text. */

interface PillRightLogoProps {
  size?: "sm" | "md" | "lg";
  showText?: boolean;
  className?: string;
}

const SIZES = {
  sm: { icon: 24, text: "text-lg" },
  md: { icon: 32, text: "text-xl" },
  lg: { icon: 40, text: "text-2xl" },
} as const;

export function PillRightLogo({ size = "md", showText = true, className = "" }: PillRightLogoProps) {
  const s = SIZES[size];

  return (
    <span className={`inline-flex items-center gap-2 ${className}`}>
      <svg
        width={s.icon}
        height={s.icon}
        viewBox="0 0 40 40"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        aria-hidden="true"
      >
        {/* Shield */}
        <path
          d="M20 3L5 10v10c0 9.39 6.4 18.17 15 20.35C28.6 38.17 35 29.39 35 20V10L20 3z"
          fill="var(--color-primary)"
        />
        {/* Inner highlight */}
        <path
          d="M20 6L8 12v8c0 7.73 5.12 14.97 12 16.72V6z"
          fill="var(--color-primary-dark)"
          opacity="0.3"
        />
        {/* Check mark */}
        <path
          d="M16 21l3 3 6-6"
          stroke="white"
          strokeWidth="2.5"
          strokeLinecap="round"
          strokeLinejoin="round"
          fill="none"
        />
        {/* Plus/cross medical symbol - small */}
        <rect x="11" y="13" width="6" height="2" rx="1" fill="var(--color-accent)" />
        <rect x="13" y="11" width="2" height="6" rx="1" fill="var(--color-accent)" />
      </svg>
      {showText && (
        <span className={`font-bold tracking-tight text-[var(--color-primary)] ${s.text}`}>
          약잘알
        </span>
      )}
    </span>
  );
}
