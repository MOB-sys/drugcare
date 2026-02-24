import 'package:yakmeogeo/shared/models/severity.dart';

/// 개별 상호작용 결과.
class InteractionResult {
  /// 아이템 A 이름.
  final String itemAName;

  /// 아이템 B 이름.
  final String itemBName;

  /// 심각도.
  final Severity severity;

  /// 상호작용 설명.
  final String? description;

  /// 상호작용 메커니즘.
  final String? mechanism;

  /// 권장 사항.
  final String? recommendation;

  /// 데이터 출처.
  final String? source;

  /// 근거 수준.
  final String? evidenceLevel;

  /// AI 생성 쉬운 설명.
  final String? aiExplanation;

  /// AI 생성 대처 방법.
  final String? aiRecommendation;

  /// [InteractionResult] 생성자.
  const InteractionResult({
    required this.itemAName,
    required this.itemBName,
    required this.severity,
    this.description,
    this.mechanism,
    this.recommendation,
    this.source,
    this.evidenceLevel,
    this.aiExplanation,
    this.aiRecommendation,
  });

  /// JSON에서 [InteractionResult]를 생성한다.
  factory InteractionResult.fromJson(Map<String, dynamic> json) {
    return InteractionResult(
      itemAName: json['item_a_name'] as String,
      itemBName: json['item_b_name'] as String,
      severity: Severity.fromJson(json['severity'] as String),
      description: json['description'] as String?,
      mechanism: json['mechanism'] as String?,
      recommendation: json['recommendation'] as String?,
      source: json['source'] as String?,
      evidenceLevel: json['evidence_level'] as String?,
      aiExplanation: json['ai_explanation'] as String?,
      aiRecommendation: json['ai_recommendation'] as String?,
    );
  }
}
