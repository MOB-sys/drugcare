"use client";

import { useState } from "react";

interface StarRatingProps {
  /** 현재 평점 값 (1-5). */
  value: number;
  /** 변경 핸들러. undefined이면 읽기 전용 모드. */
  onChange?: (value: number) => void;
  /** 별 크기 CSS 클래스. */
  size?: "sm" | "md" | "lg";
  /** 접근성 레이블. */
  label?: string;
}

const SIZE_MAP = {
  sm: "w-4 h-4",
  md: "w-5 h-5",
  lg: "w-7 h-7",
};

/** 별점 표시/입력 컴포넌트 (1-5). */
export function StarRating({
  value,
  onChange,
  size = "md",
  label = "평점",
}: StarRatingProps) {
  const [hovered, setHovered] = useState(0);
  const isInteractive = !!onChange;
  const displayValue = hovered || value;
  const sizeClass = SIZE_MAP[size];

  return (
    <div
      className="inline-flex items-center gap-0.5"
      role={isInteractive ? "radiogroup" : "img"}
      aria-label={`${label} ${value}점`}
    >
      {[1, 2, 3, 4, 5].map((star) => (
        <button
          key={star}
          type="button"
          disabled={!isInteractive}
          onClick={() => onChange?.(star)}
          onMouseEnter={() => isInteractive && setHovered(star)}
          onMouseLeave={() => isInteractive && setHovered(0)}
          className={`${isInteractive ? "cursor-pointer hover:scale-110" : "cursor-default"} transition-transform`}
          aria-label={isInteractive ? `${star}점` : undefined}
        >
          <svg
            className={`${sizeClass} ${star <= displayValue ? "text-amber-400" : "text-gray-200 dark:text-gray-700"} transition-colors`}
            fill="currentColor"
            viewBox="0 0 20 20"
          >
            <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
          </svg>
        </button>
      ))}
    </div>
  );
}
