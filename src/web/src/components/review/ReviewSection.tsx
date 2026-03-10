"use client";

import { useCallback, useEffect, useState } from "react";
import { ReviewSummaryDisplay } from "./ReviewSummary";
import { ReviewForm } from "./ReviewForm";
import { ReviewList } from "./ReviewList";
import { getReviews, getReviewSummary } from "@/lib/api/reviews";
import type { ReviewSummary } from "@/types/review";
import type { ReviewResponse } from "@/types/review";

interface ReviewSectionProps {
  itemType: string;
  itemId: number;
}

/** 리뷰 섹션 — 요약 + 작성 폼 + 목록을 통합한 래퍼. */
export function ReviewSection({ itemType, itemId }: ReviewSectionProps) {
  const [summary, setSummary] = useState<ReviewSummary | null>(null);
  const [reviews, setReviews] = useState<ReviewResponse[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(0);
  const [loading, setLoading] = useState(true);

  const fetchData = useCallback(async (p: number) => {
    setLoading(true);
    try {
      const [summaryData, reviewData] = await Promise.all([
        getReviewSummary(itemType, itemId),
        getReviews(itemType, itemId, p, 10),
      ]);
      setSummary(summaryData);
      setReviews(reviewData.items);
      setTotal(reviewData.total);
      setTotalPages(reviewData.total_pages);
      setPage(p);
    } catch {
      // 에러 시 빈 상태 유지
    } finally {
      setLoading(false);
    }
  }, [itemType, itemId]);

  useEffect(() => {
    fetchData(1);
  }, [fetchData]);

  const handleSubmitted = () => {
    fetchData(1);
  };

  const handlePageChange = (newPage: number) => {
    fetchData(newPage);
  };

  return (
    <section id="reviews" className="mt-8 scroll-mt-24">
      <h2 className="text-lg font-semibold text-[var(--color-primary)] mb-4">
        사용자 리뷰
      </h2>

      <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-6 shadow-sm space-y-6">
        {loading && !summary ? (
          <div className="text-center py-8 text-gray-400 text-sm">
            리뷰를 불러오는 중...
          </div>
        ) : (
          <>
            {summary && <ReviewSummaryDisplay summary={summary} />}

            <hr className="border-gray-100" />

            <ReviewForm
              itemType={itemType}
              itemId={itemId}
              onSubmitted={handleSubmitted}
            />

            {reviews.length > 0 && (
              <>
                <hr className="border-gray-100" />
                <ReviewList
                  reviews={reviews}
                  total={total}
                  page={page}
                  totalPages={totalPages}
                  onPageChange={handlePageChange}
                />
              </>
            )}
          </>
        )}
      </div>
    </section>
  );
}
