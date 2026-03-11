"use client";

import { StarRating } from "./StarRating";
import type { ReviewSummary as ReviewSummaryType } from "@/types/review";

interface ReviewSummaryProps {
  summary: ReviewSummaryType;
}

/** 리뷰 요약 통계 (평균 평점, 총 건수, 분포 바). */
export function ReviewSummaryDisplay({ summary }: ReviewSummaryProps) {
  const { average_rating, total_count, distribution } = summary;
  const maxCount = Math.max(...Object.values(distribution), 1);

  if (total_count === 0) {
    return (
      <div className="text-center py-6 text-gray-400 dark:text-gray-500 text-sm">
        아직 리뷰가 없습니다. 첫 번째 리뷰를 작성해보세요!
      </div>
    );
  }

  return (
    <div className="flex flex-col sm:flex-row gap-6 items-center sm:items-start">
      {/* 평균 평점 */}
      <div className="text-center shrink-0">
        <p className="text-4xl font-bold text-[var(--color-primary)]">
          {average_rating.toFixed(1)}
        </p>
        <StarRating value={Math.round(average_rating)} size="md" />
        <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
          {total_count.toLocaleString()}개 리뷰
        </p>
      </div>

      {/* 분포 바 */}
      <div className="flex-1 w-full space-y-1.5">
        {[5, 4, 3, 2, 1].map((star) => {
          const count = distribution[String(star)] || 0;
          const pct = total_count > 0 ? (count / maxCount) * 100 : 0;
          return (
            <div key={star} className="flex items-center gap-2 text-sm">
              <span className="w-6 text-right text-gray-500 dark:text-gray-400">{star}</span>
              <svg className="w-3.5 h-3.5 text-amber-400 shrink-0" fill="currentColor" viewBox="0 0 20 20">
                <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
              </svg>
              <div className="flex-1 h-2 bg-gray-100 dark:bg-gray-700 rounded-full overflow-hidden">
                <div
                  className="h-full bg-amber-400 rounded-full transition-all"
                  style={{ width: `${pct}%` }}
                />
              </div>
              <span className="w-8 text-right text-gray-400 dark:text-gray-500 text-xs">
                {count}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
