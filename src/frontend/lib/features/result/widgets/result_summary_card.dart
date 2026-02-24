import 'package:flutter/material.dart';

import 'package:yakmeogeo/core/theme/app_colors.dart';
import 'package:yakmeogeo/features/result/models/interaction_check_response.dart';

/// 상호작용 결과 요약 카드.
///
/// 체크 건수, 발견 건수를 표시하고 위험 여부에 따라 색상을 변경한다.
class ResultSummaryCard extends StatelessWidget {
  /// [ResultSummaryCard] 생성자.
  ///
  /// [response] — 상호작용 체크 전체 응답.
  const ResultSummaryCard({super.key, required this.response});

  /// 상호작용 체크 응답.
  final InteractionCheckResponse response;

  @override
  Widget build(BuildContext context) {
    final hasInteractions = response.interactionsFound > 0;
    final hasDanger = response.hasDanger;

    final Color bgColor;
    final Color iconColor;
    final IconData iconData;
    final String statusText;

    if (hasDanger) {
      bgColor = AppColors.dangerBg;
      iconColor = AppColors.danger;
      iconData = Icons.dangerous;
      statusText = '위험한 조합이 포함되어 있습니다!';
    } else if (hasInteractions) {
      bgColor = AppColors.warningBg;
      iconColor = AppColors.warning;
      iconData = Icons.warning_amber_rounded;
      statusText = '주의가 필요한 조합이 있습니다.';
    } else {
      bgColor = AppColors.safeBg;
      iconColor = AppColors.safe;
      iconData = Icons.check_circle;
      statusText = '확인된 상호작용이 없습니다.';
    }

    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: Container(
        width: double.infinity,
        padding: const EdgeInsets.all(20),
        decoration: BoxDecoration(
          color: bgColor,
          borderRadius: BorderRadius.circular(12),
        ),
        child: Column(
          children: [
            Icon(iconData, size: 40, color: iconColor),
            const SizedBox(height: 12),
            Text(
              '총 ${response.totalChecked}쌍 확인 / ${response.interactionsFound}건 발견',
              style: const TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.w600,
                color: AppColors.textPrimary,
              ),
            ),
            const SizedBox(height: 6),
            Text(
              statusText,
              style: TextStyle(
                fontSize: 14,
                fontWeight: FontWeight.w500,
                color: iconColor,
              ),
              textAlign: TextAlign.center,
            ),
          ],
        ),
      ),
    );
  }
}
