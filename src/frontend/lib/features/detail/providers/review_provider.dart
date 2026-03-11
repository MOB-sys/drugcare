import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'package:pillright/core/providers/service_providers.dart';
import 'package:pillright/features/detail/models/review.dart';

/// 리뷰 조회 키.
class ReviewKey {
  /// 아이템 유형 (drug / supplement).
  final String itemType;

  /// 아이템 ID.
  final int itemId;

  /// [ReviewKey] 생성자.
  const ReviewKey(this.itemType, this.itemId);

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is ReviewKey &&
          itemType == other.itemType &&
          itemId == other.itemId;

  @override
  int get hashCode => Object.hash(itemType, itemId);
}

/// 리뷰 통계 프로바이더.
final reviewSummaryProvider =
    FutureProvider.family<ReviewSummary, ReviewKey>((ref, key) async {
  final service = ref.read(reviewServiceProvider);
  return service.getReviewSummary(key.itemType, key.itemId);
});

/// 리뷰 목록 상태.
class ReviewListState {
  /// 리뷰 목록 (비동기 값).
  final AsyncValue<List<Review>> reviews;

  /// 현재 페이지.
  final int currentPage;

  /// 전체 페이지 수.
  final int totalPages;

  /// 추가 로딩 중 여부.
  final bool isLoadingMore;

  /// [ReviewListState] 생성자.
  const ReviewListState({
    this.reviews = const AsyncValue.loading(),
    this.currentPage = 0,
    this.totalPages = 1,
    this.isLoadingMore = false,
  });

  /// 더 불러올 수 있는지 여부.
  bool get hasMore => currentPage < totalPages;

  /// 상태를 복사하면서 일부 필드만 변경한다.
  ReviewListState copyWith({
    AsyncValue<List<Review>>? reviews,
    int? currentPage,
    int? totalPages,
    bool? isLoadingMore,
  }) {
    return ReviewListState(
      reviews: reviews ?? this.reviews,
      currentPage: currentPage ?? this.currentPage,
      totalPages: totalPages ?? this.totalPages,
      isLoadingMore: isLoadingMore ?? this.isLoadingMore,
    );
  }
}

/// 리뷰 목록 상태 관리 노티파이어.
///
/// 페이지네이션, 작성, 도움됨, 삭제를 처리한다.
class ReviewListNotifier extends StateNotifier<ReviewListState> {
  /// [ReviewListNotifier] 생성자.
  ReviewListNotifier(this._ref, this._key)
      : super(const ReviewListState()) {
    loadReviews();
  }

  /// Riverpod Ref 참조.
  final Ref _ref;

  /// 리뷰 조회 키.
  final ReviewKey _key;

  /// 리뷰 목록을 서버에서 가져온다.
  Future<void> loadReviews() async {
    state = state.copyWith(
      reviews: const AsyncValue.loading(),
      currentPage: 0,
    );

    try {
      final service = _ref.read(reviewServiceProvider);
      final result = await service.getReviews(
        _key.itemType,
        _key.itemId,
      );

      state = state.copyWith(
        reviews: AsyncValue.data(result.items),
        currentPage: result.page,
        totalPages: result.totalPages,
      );
    } catch (e, st) {
      state = state.copyWith(reviews: AsyncValue.error(e, st));
    }
  }

  /// 다음 페이지를 로드한다.
  Future<void> loadMore() async {
    if (!state.hasMore || state.isLoadingMore) return;

    state = state.copyWith(isLoadingMore: true);

    try {
      final service = _ref.read(reviewServiceProvider);
      final result = await service.getReviews(
        _key.itemType,
        _key.itemId,
        page: state.currentPage + 1,
      );

      final current = state.reviews.valueOrNull ?? [];
      state = state.copyWith(
        reviews: AsyncValue.data([...current, ...result.items]),
        currentPage: result.page,
        totalPages: result.totalPages,
        isLoadingMore: false,
      );
    } catch (e, st) {
      state = state.copyWith(
        reviews: AsyncValue.error(e, st),
        isLoadingMore: false,
      );
    }
  }

  /// 리뷰를 작성하고 목록을 새로고침한다.
  Future<void> createReview({
    required int rating,
    int? effectiveness,
    int? easeOfUse,
    String? comment,
  }) async {
    final service = _ref.read(reviewServiceProvider);
    await service.createReview(
      itemType: _key.itemType,
      itemId: _key.itemId,
      rating: rating,
      effectiveness: effectiveness,
      easeOfUse: easeOfUse,
      comment: comment,
    );

    // 목록 및 통계 새로고침.
    await loadReviews();
    _ref.invalidate(reviewSummaryProvider(_key));
  }

  /// 리뷰에 도움됨을 표시한다.
  Future<void> markHelpful(int reviewId) async {
    final service = _ref.read(reviewServiceProvider);
    await service.markHelpful(reviewId);
    await loadReviews();
  }

  /// 리뷰를 삭제한다.
  Future<void> deleteReview(int reviewId) async {
    final service = _ref.read(reviewServiceProvider);
    await service.deleteReview(reviewId);

    await loadReviews();
    _ref.invalidate(reviewSummaryProvider(_key));
  }
}

/// 리뷰 목록 프로바이더.
final reviewListProvider = StateNotifierProvider.family<
    ReviewListNotifier, ReviewListState, ReviewKey>((ref, key) {
  return ReviewListNotifier(ref, key);
});
