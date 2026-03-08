import 'dart:math';

import 'package:flutter/material.dart';

import 'package:pillright/core/constants/app_constants.dart';
import 'package:pillright/core/theme/app_colors.dart';

/// 오늘의 건강팁 카드 위젯.
///
/// 매일 같은 날짜에는 같은 팁을 표시한다 (날짜 기반 시드).
class HealthTipCard extends StatelessWidget {
  /// [HealthTipCard] 생성자.
  const HealthTipCard({super.key});

  /// 오늘 날짜를 시드로 사용하여 건강팁 인덱스를 결정한다.
  String _todayTip() {
    final now = DateTime.now();
    final seed = now.year * 10000 + now.month * 100 + now.day;
    final index = Random(seed).nextInt(AppConstants.healthTips.length);
    return AppConstants.healthTips[index];
  }

  @override
  Widget build(BuildContext context) {
    final tip = _todayTip();

    return Card(
      elevation: 0,
      color: AppColors.infoBg,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Icon(
              Icons.lightbulb_outline,
              color: AppColors.info,
              size: 24,
            ),
            const SizedBox(width: 12),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    '오늘의 건강팁',
                    style: TextStyle(
                      fontSize: 14,
                      fontWeight: FontWeight.w600,
                      color: AppColors.info,
                    ),
                  ),
                  const SizedBox(height: 6),
                  Text(
                    tip,
                    style: const TextStyle(
                      fontSize: 13,
                      color: AppColors.textPrimary,
                      height: 1.5,
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
