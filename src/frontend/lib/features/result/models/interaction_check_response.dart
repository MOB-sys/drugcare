import 'package:pillright/features/result/models/interaction_result.dart';

/// 상호작용 체크 전체 응답.
class InteractionCheckResponse {
  /// 총 체크 건수.
  final int totalChecked;

  /// 발견된 상호작용 수.
  final int interactionsFound;

  /// 위험 등급 상호작용 존재 여부.
  final bool hasDanger;

  /// 상호작용 결과 목록.
  final List<InteractionResult> results;

  /// 면책조항.
  final String disclaimer;

  /// [InteractionCheckResponse] 생성자.
  const InteractionCheckResponse({
    required this.totalChecked,
    required this.interactionsFound,
    required this.hasDanger,
    required this.results,
    required this.disclaimer,
  });

  /// JSON에서 [InteractionCheckResponse]를 생성한다.
  factory InteractionCheckResponse.fromJson(Map<String, dynamic> json) {
    return InteractionCheckResponse(
      totalChecked: json['total_checked'] as int,
      interactionsFound: json['interactions_found'] as int,
      hasDanger: json['has_danger'] as bool,
      results: (json['results'] as List)
          .map((e) => InteractionResult.fromJson(e as Map<String, dynamic>))
          .toList(),
      disclaimer: json['disclaimer'] as String,
    );
  }
}
