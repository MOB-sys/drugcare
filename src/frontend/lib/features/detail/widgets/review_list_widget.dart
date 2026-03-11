import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'package:pillright/core/theme/app_colors.dart';
import 'package:pillright/features/detail/models/review.dart';
import 'package:pillright/features/detail/providers/review_provider.dart';
import 'package:pillright/features/detail/widgets/star_rating.dart';

/// 리뷰 목록 위젯.
///
/// 리뷰 카드 리스트와 페이지네이션 "더 보기" 버튼을 표시한다.
class ReviewListWidget extends ConsumerWidget {
  /// 아이템 유형.
  final String itemType;

  /// 아이템 ID.
  final int itemId;

  /// 현재 디바이스 ID (본인 리뷰 삭제 표시용).
  final String? currentDeviceId;

  /// [ReviewListWidget] 생성자.
  const ReviewListWidget({
    super.key,
    required this.itemType,
    required this.itemId,
    this.currentDeviceId,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final key = ReviewKey(itemType, itemId);
    final reviewState = ref.watch(reviewListProvider(key));

    return reviewState.reviews.when(
      loading: () => const Center(
        child: Padding(
          padding: EdgeInsets.all(16),
          child: CircularProgressIndicator(),
        ),
      ),
      error: (error, _) => Padding(
        padding: const EdgeInsets.all(16),
        child: Text(
          '리뷰를 불러올 수 없습니다.',
          style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                color: AppColors.textSecondary,
              ),
        ),
      ),
      data: (reviews) {
        if (reviews.isEmpty) {
          return const SizedBox.shrink();
        }

        return Column(
          children: [
            ...reviews.map((review) => _ReviewCard(
                  review: review,
                  isOwn: review.deviceId == currentDeviceId,
                  onHelpful: () {
                    ref
                        .read(reviewListProvider(key).notifier)
                        .markHelpful(review.id);
                  },
                  onDelete: () {
                    ref
                        .read(reviewListProvider(key).notifier)
                        .deleteReview(review.id);
                  },
                )),
            if (reviewState.hasMore)
              Padding(
                padding: const EdgeInsets.symmetric(vertical: 8),
                child: reviewState.isLoadingMore
                    ? const Center(child: CircularProgressIndicator())
                    : TextButton(
                        onPressed: () {
                          ref
                              .read(reviewListProvider(key).notifier)
                              .loadMore();
                        },
                        child: const Text('더 보기'),
                      ),
              ),
          ],
        );
      },
    );
  }
}

class _ReviewCard extends StatelessWidget {
  final Review review;
  final bool isOwn;
  final VoidCallback onHelpful;
  final VoidCallback onDelete;

  const _ReviewCard({
    required this.review,
    required this.isOwn,
    required this.onHelpful,
    required this.onDelete,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Card(
      margin: const EdgeInsets.only(bottom: 8),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // 별점 + 날짜 + 삭제.
            Row(
              children: [
                StarRating(rating: review.rating, size: 16),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    _formatDate(review.createdAt),
                    style: theme.textTheme.bodySmall?.copyWith(
                      color: AppColors.textSecondary,
                    ),
                  ),
                ),
                if (isOwn)
                  IconButton(
                    icon: const Icon(Icons.delete_outline, size: 18),
                    color: AppColors.textSecondary,
                    padding: EdgeInsets.zero,
                    constraints: const BoxConstraints(),
                    tooltip: '삭제',
                    onPressed: () => _confirmDelete(context),
                  ),
              ],
            ),
            // 코멘트.
            if (review.comment != null && review.comment!.isNotEmpty) ...[
              const SizedBox(height: 8),
              Text(
                review.comment!,
                style: theme.textTheme.bodyMedium,
              ),
            ],
            const SizedBox(height: 8),
            // 도움됨 버튼.
            Row(
              children: [
                InkWell(
                  onTap: onHelpful,
                  borderRadius: BorderRadius.circular(4),
                  child: Padding(
                    padding: const EdgeInsets.symmetric(
                      horizontal: 8,
                      vertical: 4,
                    ),
                    child: Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        const Icon(
                          Icons.thumb_up_outlined,
                          size: 14,
                          color: AppColors.textSecondary,
                        ),
                        const SizedBox(width: 4),
                        Text(
                          '도움됨 ${review.helpfulCount}',
                          style: theme.textTheme.bodySmall?.copyWith(
                            color: AppColors.textSecondary,
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  /// 삭제 확인 다이얼로그를 표시한다.
  void _confirmDelete(BuildContext context) {
    showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('리뷰 삭제'),
        content: const Text('이 리뷰를 삭제하시겠습니까?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(ctx).pop(),
            child: const Text('취소'),
          ),
          TextButton(
            onPressed: () {
              Navigator.of(ctx).pop();
              onDelete();
            },
            child: const Text('삭제'),
          ),
        ],
      ),
    );
  }

  /// ISO 날짜 문자열을 간략하게 포맷한다.
  String _formatDate(String isoDate) {
    try {
      final dt = DateTime.parse(isoDate);
      return '${dt.year}.${dt.month.toString().padLeft(2, '0')}.${dt.day.toString().padLeft(2, '0')}';
    } catch (_) {
      return isoDate;
    }
  }
}
