import 'package:dio/dio.dart';

import 'package:pillright/core/constants/api_constants.dart';
import 'package:pillright/core/utils/api_response_parser.dart';
import 'package:pillright/features/detail/models/review.dart';
import 'package:pillright/shared/models/paginated_result.dart';

/// 리뷰 API 서비스.
class ReviewService {
  /// Dio HTTP 클라이언트.
  final Dio _dio;

  /// [ReviewService] 생성자.
  ReviewService(this._dio);

  /// 리뷰 목록을 조회한다.
  ///
  /// [itemType] 아이템 유형, [itemId] 아이템 ID.
  /// [page] 페이지 번호, [pageSize] 페이지 크기.
  Future<PaginatedResult<Review>> getReviews(
    String itemType,
    int itemId, {
    int page = 1,
    int pageSize = 10,
  }) async {
    final response = await _dio.get(
      ApiConstants.reviewList(itemType, itemId),
      queryParameters: {'page': page, 'page_size': pageSize},
    );

    return ApiResponseParser.parse(
      response.data as Map<String, dynamic>,
      (data) => PaginatedResult.fromJson(
        data as Map<String, dynamic>,
        Review.fromJson,
      ),
    );
  }

  /// 리뷰 통계를 조회한다.
  ///
  /// [itemType] 아이템 유형, [itemId] 아이템 ID.
  Future<ReviewSummary> getReviewSummary(
    String itemType,
    int itemId,
  ) async {
    final response = await _dio.get(
      ApiConstants.reviewSummary(itemType, itemId),
    );

    return ApiResponseParser.parse(
      response.data as Map<String, dynamic>,
      (data) => ReviewSummary.fromJson(data as Map<String, dynamic>),
    );
  }

  /// 리뷰를 작성한다.
  ///
  /// [itemType] 아이템 유형, [itemId] 아이템 ID, [rating] 별점(1~5).
  /// [effectiveness] 효과 점수, [easeOfUse] 편의성 점수, [comment] 코멘트.
  Future<Review> createReview({
    required String itemType,
    required int itemId,
    required int rating,
    int? effectiveness,
    int? easeOfUse,
    String? comment,
  }) async {
    final response = await _dio.post(
      ApiConstants.reviews,
      data: {
        'item_type': itemType,
        'item_id': itemId,
        'rating': rating,
        if (effectiveness != null) 'effectiveness': effectiveness,
        if (easeOfUse != null) 'ease_of_use': easeOfUse,
        if (comment != null && comment.isNotEmpty) 'comment': comment,
      },
    );

    return ApiResponseParser.parse(
      response.data as Map<String, dynamic>,
      (data) => Review.fromJson(data as Map<String, dynamic>),
    );
  }

  /// 리뷰에 도움됨을 표시한다.
  ///
  /// [reviewId] 리뷰 ID.
  Future<void> markHelpful(int reviewId) async {
    final response = await _dio.post(
      ApiConstants.reviewHelpful(reviewId),
    );

    ApiResponseParser.parse(
      response.data as Map<String, dynamic>,
      (data) => data,
    );
  }

  /// 리뷰를 삭제한다.
  ///
  /// [reviewId] 리뷰 ID.
  Future<void> deleteReview(int reviewId) async {
    final response = await _dio.delete(
      ApiConstants.reviewDelete(reviewId),
    );

    ApiResponseParser.parse(
      response.data as Map<String, dynamic>,
      (data) => data,
    );
  }
}
