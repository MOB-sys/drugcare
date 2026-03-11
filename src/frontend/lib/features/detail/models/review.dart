/// 리뷰 응답 모델.
class Review {
  /// 리뷰 ID.
  final int id;

  /// 작성자 디바이스 ID.
  final String deviceId;

  /// 아이템 유형 (drug / supplement).
  final String itemType;

  /// 아이템 ID.
  final int itemId;

  /// 별점 (1~5).
  final int rating;

  /// 효과 점수 (1~5, 선택).
  final int? effectiveness;

  /// 사용 편의성 점수 (1~5, 선택).
  final int? easeOfUse;

  /// 리뷰 코멘트 (선택).
  final String? comment;

  /// 도움됨 수.
  final int helpfulCount;

  /// 생성 일시.
  final String createdAt;

  /// 수정 일시.
  final String? updatedAt;

  /// [Review] 생성자.
  const Review({
    required this.id,
    required this.deviceId,
    required this.itemType,
    required this.itemId,
    required this.rating,
    this.effectiveness,
    this.easeOfUse,
    this.comment,
    this.helpfulCount = 0,
    required this.createdAt,
    this.updatedAt,
  });

  /// JSON에서 [Review]를 생성한다.
  factory Review.fromJson(Map<String, dynamic> json) {
    return Review(
      id: json['id'] as int,
      deviceId: json['device_id'] as String,
      itemType: json['item_type'] as String,
      itemId: json['item_id'] as int,
      rating: json['rating'] as int,
      effectiveness: json['effectiveness'] as int?,
      easeOfUse: json['ease_of_use'] as int?,
      comment: json['comment'] as String?,
      helpfulCount: json['helpful_count'] as int? ?? 0,
      createdAt: json['created_at'] as String,
      updatedAt: json['updated_at'] as String?,
    );
  }
}

/// 리뷰 통계 모델.
class ReviewSummary {
  /// 평균 별점.
  final double averageRating;

  /// 전체 리뷰 수.
  final int totalCount;

  /// 별점 분포 (키: "1"~"5", 값: 개수).
  final Map<String, int> distribution;

  /// [ReviewSummary] 생성자.
  const ReviewSummary({
    required this.averageRating,
    required this.totalCount,
    required this.distribution,
  });

  /// JSON에서 [ReviewSummary]를 생성한다.
  factory ReviewSummary.fromJson(Map<String, dynamic> json) {
    return ReviewSummary(
      averageRating: (json['average_rating'] as num).toDouble(),
      totalCount: json['total_count'] as int,
      distribution: (json['distribution'] as Map<String, dynamic>).map(
        (k, v) => MapEntry(k, v as int),
      ),
    );
  }
}
