import 'package:flutter/material.dart';

import 'package:yakmeogeo/core/theme/app_colors.dart';
import 'package:yakmeogeo/features/result/models/interaction_result.dart';
import 'package:yakmeogeo/shared/widgets/common/severity_badge.dart';

/// 개별 상호작용 결과 카드.
///
/// 신호등 배경색으로 심각도를 표시하고, 확장 영역에 상세 정보를 제공한다.
class InteractionResultCard extends StatefulWidget {
  /// [InteractionResultCard] 생성자.
  ///
  /// [result] — 개별 상호작용 결과 데이터.
  const InteractionResultCard({super.key, required this.result});

  /// 상호작용 결과.
  final InteractionResult result;

  @override
  State<InteractionResultCard> createState() => _InteractionResultCardState();
}

class _InteractionResultCardState extends State<InteractionResultCard> {
  bool _isExpanded = false;

  @override
  Widget build(BuildContext context) {
    final result = widget.result;

    return Card(
      elevation: 1,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      clipBehavior: Clip.antiAlias,
      child: Container(
        decoration: BoxDecoration(
          color: result.severity.backgroundColor,
          borderRadius: BorderRadius.circular(12),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // 메인 영역
            InkWell(
              onTap: () => setState(() => _isExpanded = !_isExpanded),
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // 제목 행: 약A ↔ 약B + 심각도 배지
                    Row(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Expanded(
                          child: Text(
                            '${result.itemAName} ↔ ${result.itemBName}',
                            style: const TextStyle(
                              fontSize: 15,
                              fontWeight: FontWeight.w600,
                              color: AppColors.textPrimary,
                            ),
                          ),
                        ),
                        const SizedBox(width: 8),
                        SeverityBadge(severity: result.severity),
                      ],
                    ),
                    const SizedBox(height: 8),
                    // 설명
                    if (result.description != null)
                      Text(
                        result.description!,
                        style: const TextStyle(
                          fontSize: 13,
                          color: AppColors.textPrimary,
                          height: 1.5,
                        ),
                      ),
                    const SizedBox(height: 8),
                    // 확장 토글
                    Row(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Text(
                          _isExpanded ? '접기' : '상세 보기',
                          style: TextStyle(
                            fontSize: 12,
                            color: result.severity.color,
                            fontWeight: FontWeight.w500,
                          ),
                        ),
                        Icon(
                          _isExpanded
                              ? Icons.keyboard_arrow_up
                              : Icons.keyboard_arrow_down,
                          size: 18,
                          color: result.severity.color,
                        ),
                      ],
                    ),
                  ],
                ),
              ),
            ),

            // 확장 상세 영역
            if (_isExpanded)
              Container(
                width: double.infinity,
                padding: const EdgeInsets.fromLTRB(16, 0, 16, 16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Divider(height: 1),
                    const SizedBox(height: 12),
                    if (result.mechanism != null)
                      _DetailRow(
                        label: '작용 기전',
                        value: result.mechanism!,
                      ),
                    if (result.recommendation != null)
                      _DetailRow(
                        label: '권장 사항',
                        value: result.recommendation!,
                      ),
                    if (result.source != null)
                      _DetailRow(
                        label: '출처',
                        value: result.source!,
                      ),
                    if (result.evidenceLevel != null)
                      _DetailRow(
                        label: '근거 수준',
                        value: result.evidenceLevel!,
                      ),
                    // AI 쉬운 설명 섹션
                    if (result.aiExplanation != null) ...[
                      const SizedBox(height: 8),
                      const Divider(height: 1),
                      const SizedBox(height: 12),
                      Row(
                        children: [
                          Icon(
                            Icons.auto_awesome,
                            size: 16,
                            color: result.severity.color,
                          ),
                          const SizedBox(width: 4),
                          Text(
                            'AI 쉬운 설명',
                            style: TextStyle(
                              fontSize: 12,
                              fontWeight: FontWeight.w600,
                              color: result.severity.color,
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 6),
                      Text(
                        result.aiExplanation!,
                        style: const TextStyle(
                          fontSize: 13,
                          color: AppColors.textPrimary,
                          height: 1.5,
                        ),
                      ),
                      if (result.aiRecommendation != null)
                        Padding(
                          padding: const EdgeInsets.only(top: 8),
                          child: _DetailRow(
                            label: 'AI 대처 방법',
                            value: result.aiRecommendation!,
                          ),
                        ),
                    ],
                  ],
                ),
              ),
          ],
        ),
      ),
    );
  }
}

/// 상세 정보 행 위젯.
class _DetailRow extends StatelessWidget {
  const _DetailRow({
    required this.label,
    required this.value,
  });

  final String label;
  final String value;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 10),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            label,
            style: const TextStyle(
              fontSize: 12,
              fontWeight: FontWeight.w600,
              color: AppColors.textSecondary,
            ),
          ),
          const SizedBox(height: 2),
          Text(
            value,
            style: const TextStyle(
              fontSize: 13,
              color: AppColors.textPrimary,
              height: 1.4,
            ),
          ),
        ],
      ),
    );
  }
}
