"use client";

import { useState } from "react";
import { StarRating } from "./StarRating";
import { markHelpful } from "@/lib/api/reviews";
import type { ReviewResponse } from "@/types/review";

interface ReviewListProps {
  reviews: ReviewResponse[];
  total: number;
  page: number;
  totalPages: number;
  onPageChange: (page: number) => void;
}

/** 리뷰 목록 (페이지네이션 + 도움됨 버튼). */
export function ReviewList({
  reviews,
  total,
  page,
  totalPages,
  onPageChange,
}: ReviewListProps) {
  const [helpedIds, setHelpedIds] = useState<Set<number>>(new Set());

  if (reviews.length === 0) {
    return null;
  }

  const handleHelpful = async (reviewId: number) => {
    if (helpedIds.has(reviewId)) return;
    try {
      await markHelpful(reviewId);
      setHelpedIds((prev) => new Set(prev).add(reviewId));
    } catch {
      // 실패 시 무시
    }
  };

  const formatDate = (dateStr: string) => {
    const d = new Date(dateStr);
    return d.toLocaleDateString("ko-KR", {
      year: "numeric",
      month: "short",
      day: "numeric",
    });
  };

  return (
    <div className="space-y-3">
      <p className="text-sm text-gray-500 dark:text-gray-400">
        총 {total.toLocaleString()}개 리뷰
      </p>

      {reviews.map((review) => (
        <div
          key={review.id}
          className="p-4 border border-gray-100 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800"
        >
          <div className="flex items-center justify-between mb-2">
            <StarRating value={review.rating} size="sm" />
            <span className="text-xs text-gray-400 dark:text-gray-500">
              {formatDate(review.created_at)}
            </span>
          </div>

          {/* 세부 평점 */}
          {(review.effectiveness || review.ease_of_use) && (
            <div className="flex gap-4 mb-2 text-xs text-gray-500 dark:text-gray-400">
              {review.effectiveness && (
                <span>효과 {review.effectiveness}/5</span>
              )}
              {review.ease_of_use && (
                <span>편의성 {review.ease_of_use}/5</span>
              )}
            </div>
          )}

          {review.comment && (
            <p className="text-sm text-gray-700 dark:text-gray-300 mb-2 whitespace-pre-line">
              {review.comment}
            </p>
          )}

          <button
            type="button"
            onClick={() => handleHelpful(review.id)}
            disabled={helpedIds.has(review.id)}
            className={`text-xs px-2 py-1 rounded border transition-colors ${
              helpedIds.has(review.id)
                ? "border-[var(--color-primary-100)] text-[var(--color-primary)] bg-[var(--color-primary-50)]"
                : "border-gray-200 dark:border-gray-700 text-gray-400 dark:text-gray-500 hover:text-[var(--color-primary)] hover:border-[var(--color-primary-100)]"
            }`}
          >
            도움됨 {review.helpful_count + (helpedIds.has(review.id) ? 1 : 0)}
          </button>
        </div>
      ))}

      {/* 페이지네이션 */}
      {totalPages > 1 && (
        <div className="flex justify-center gap-1 pt-2">
          <button
            type="button"
            onClick={() => onPageChange(page - 1)}
            disabled={page <= 1}
            className="px-3 py-1.5 text-sm border border-gray-200 dark:border-gray-700 rounded-lg disabled:opacity-30 hover:bg-gray-50 dark:hover:bg-gray-700"
          >
            이전
          </button>
          <span className="px-3 py-1.5 text-sm text-gray-500 dark:text-gray-400">
            {page} / {totalPages}
          </span>
          <button
            type="button"
            onClick={() => onPageChange(page + 1)}
            disabled={page >= totalPages}
            className="px-3 py-1.5 text-sm border border-gray-200 dark:border-gray-700 rounded-lg disabled:opacity-30 hover:bg-gray-50 dark:hover:bg-gray-700"
          >
            다음
          </button>
        </div>
      )}
    </div>
  );
}
