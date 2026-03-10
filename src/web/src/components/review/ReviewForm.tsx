"use client";

import { useState } from "react";
import { StarRating } from "./StarRating";
import { createReview } from "@/lib/api/reviews";
import { executeRecaptcha } from "@/lib/recaptcha";

interface ReviewFormProps {
  itemType: string;
  itemId: number;
  onSubmitted: () => void;
}

/** 리뷰 작성 폼 컴포넌트. */
export function ReviewForm({ itemType, itemId, onSubmitted }: ReviewFormProps) {
  const [rating, setRating] = useState(0);
  const [effectiveness, setEffectiveness] = useState(0);
  const [easeOfUse, setEaseOfUse] = useState(0);
  const [comment, setComment] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (rating === 0) {
      setError("평점을 선택해주세요.");
      return;
    }
    setSubmitting(true);
    setError(null);

    try {
      const recaptchaToken = await executeRecaptcha("submit_review");
      await createReview(itemType, itemId, {
        rating,
        effectiveness: effectiveness || null,
        ease_of_use: easeOfUse || null,
        comment: comment.trim() || null,
        recaptcha_token: recaptchaToken,
      });
      setRating(0);
      setEffectiveness(0);
      setEaseOfUse(0);
      setComment("");
      onSubmitted();
    } catch {
      setError("리뷰 등록에 실패했습니다. 다시 시도해주세요.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300">리뷰 작성</h3>

      {/* 전체 평점 */}
      <div>
        <label className="block text-xs text-gray-500 dark:text-gray-400 mb-1">
          전체 평점 <span className="text-red-400">*</span>
        </label>
        <StarRating value={rating} onChange={setRating} size="lg" label="전체 평점" />
      </div>

      {/* 세부 평점 */}
      <div className="flex flex-wrap gap-6">
        <div>
          <label className="block text-xs text-gray-500 dark:text-gray-400 mb-1">효과</label>
          <StarRating value={effectiveness} onChange={setEffectiveness} size="sm" label="효과" />
        </div>
        <div>
          <label className="block text-xs text-gray-500 dark:text-gray-400 mb-1">복용 편의성</label>
          <StarRating value={easeOfUse} onChange={setEaseOfUse} size="sm" label="복용 편의성" />
        </div>
      </div>

      {/* 코멘트 */}
      <div>
        <label className="block text-xs text-gray-500 dark:text-gray-400 mb-1">
          한줄평 (선택, 최대 500자)
        </label>
        <textarea
          value={comment}
          onChange={(e) => setComment(e.target.value.slice(0, 500))}
          placeholder="복용 경험을 공유해주세요..."
          rows={3}
          maxLength={500}
          className="w-full px-3 py-2 border border-gray-200 dark:border-gray-700 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]/30 focus:border-[var(--color-primary)] resize-none bg-white dark:bg-gray-800 dark:text-gray-100"
        />
        <p className="text-xs text-gray-400 text-right">{comment.length}/500</p>
      </div>

      {error && <p className="text-sm text-red-500">{error}</p>}

      <button
        type="submit"
        disabled={submitting || rating === 0}
        className="px-6 py-2 bg-[var(--color-primary)] text-white text-sm font-medium rounded-lg hover:bg-[var(--color-primary-600)] disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
      >
        {submitting ? "등록 중..." : "리뷰 등록"}
      </button>

      <p className="text-xs text-gray-400 dark:text-gray-500">
        리뷰는 다른 사용자에게 도움이 됩니다. 의사/약사의 전문적 판단을 대체하지 않습니다.
      </p>
    </form>
  );
}
