import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'package:pillright/core/theme/app_colors.dart';
import 'package:pillright/features/detail/models/review.dart';
import 'package:pillright/features/detail/providers/review_provider.dart';
import 'package:pillright/features/detail/widgets/star_rating.dart';

/// 리뷰 통계 요약 위젯.
///
/// 평균 별점, 총 리뷰 수, 별점 분포 바 차트를 표시한다.
class ReviewSummaryWidget extends ConsumerWidget {
  /// 아이템 유형.
  final String itemType;

  /// 아이템 ID.
  final int itemId;

  /// [ReviewSummaryWidget] 생성자.
  const ReviewSummaryWidget({
    super.key,
    required this.itemType,
    required this.itemId,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final key = ReviewKey(itemType, itemId);
    final summaryAsync = ref.watch(reviewSummaryProvider(key));

    return summaryAsync.when(
      loading: () => const Center(
        child: Padding(
          padding: EdgeInsets.all(16),
          child: CircularProgressIndicator(),
        ),
      ),
      error: (error, _) => Padding(
        padding: const EdgeInsets.all(16),
        child: Text(
          '리뷰 통계를 불러올 수 없습니다.',
          style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                color: AppColors.textSecondary,
              ),
        ),
      ),
      data: (summary) => _SummaryContent(summary: summary),
    );
  }
}

class _SummaryContent extends StatelessWidget {
  final ReviewSummary summary;

  const _SummaryContent({required this.summary});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    if (summary.totalCount == 0) {
      return Padding(
        padding: const EdgeInsets.symmetric(vertical: 8),
        child: Text(
          '아직 리뷰가 없습니다. 첫 번째 리뷰를 작성해 보세요!',
          style: theme.textTheme.bodyMedium?.copyWith(
            color: AppColors.textSecondary,
          ),
        ),
      );
    }

    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // 평균 별점 + 총 개수.
        Column(
          children: [
            Text(
              summary.averageRating.toStringAsFixed(1),
              style: theme.textTheme.headlineLarge?.copyWith(
                fontWeight: FontWeight.w700,
              ),
            ),
            const SizedBox(height: 4),
            StarRating(rating: summary.averageRating.round()),
            const SizedBox(height: 4),
            Text(
              '${summary.totalCount}개 리뷰',
              style: theme.textTheme.bodySmall?.copyWith(
                color: AppColors.textSecondary,
              ),
            ),
          ],
        ),
        const SizedBox(width: 24),
        // 별점 분포 바 차트.
        Expanded(
          child: Column(
            children: List.generate(5, (index) {
              final star = 5 - index;
              final count = summary.distribution['$star'] ?? 0;
              final ratio = summary.totalCount > 0
                  ? count / summary.totalCount
                  : 0.0;

              return Padding(
                padding: const EdgeInsets.symmetric(vertical: 2),
                child: Row(
                  children: [
                    SizedBox(
                      width: 16,
                      child: Text(
                        '$star',
                        style: theme.textTheme.bodySmall?.copyWith(
                          color: AppColors.textSecondary,
                        ),
                        textAlign: TextAlign.center,
                      ),
                    ),
                    const SizedBox(width: 4),
                    const Icon(Icons.star, size: 12, color: Colors.amber),
                    const SizedBox(width: 4),
                    Expanded(
                      child: ClipRRect(
                        borderRadius: BorderRadius.circular(4),
                        child: LinearProgressIndicator(
                          value: ratio,
                          minHeight: 8,
                          backgroundColor: AppColors.dividerLight,
                          valueColor: const AlwaysStoppedAnimation<Color>(
                            Colors.amber,
                          ),
                        ),
                      ),
                    ),
                    const SizedBox(width: 8),
                    SizedBox(
                      width: 24,
                      child: Text(
                        '$count',
                        style: theme.textTheme.bodySmall?.copyWith(
                          color: AppColors.textSecondary,
                        ),
                        textAlign: TextAlign.end,
                      ),
                    ),
                  ],
                ),
              );
            }),
          ),
        ),
      ],
    );
  }
}
