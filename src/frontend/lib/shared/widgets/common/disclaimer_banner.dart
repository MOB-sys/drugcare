import 'package:flutter/material.dart';

import 'package:pillright/core/constants/app_constants.dart';

/// 의료 면책조항 배너 위젯.
///
/// 모든 결과 화면 하단에 표시되는 경고 배너.
/// 라이트/다크 모드 모두 지원.
class DisclaimerBanner extends StatelessWidget {
  /// [DisclaimerBanner] 생성자.
  ///
  /// [onTap] — 배너 탭 시 상세 면책조항 표시 콜백 (선택).
  const DisclaimerBanner({super.key, this.onTap});

  /// 배너 탭 시 콜백.
  final VoidCallback? onTap;

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final bgColor = isDark ? const Color(0xFF3B2E08) : const Color(0xFFFFF8E1);
    final borderColor =
        isDark ? const Color(0xFF6B5A1E) : const Color(0xFFFFE082);
    final iconColor =
        isDark ? const Color(0xFFFBBF24) : const Color(0xFFF9A825);
    final textColor =
        isDark ? const Color(0xFFE2D6A0) : const Color(0xFF5D4037);

    return GestureDetector(
      onTap: onTap,
      child: Container(
        width: double.infinity,
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
        decoration: BoxDecoration(
          color: bgColor,
          borderRadius: BorderRadius.circular(8),
          border: Border.all(color: borderColor),
        ),
        child: Row(
          children: [
            Icon(
              Icons.warning_amber_rounded,
              color: iconColor,
              size: 20,
            ),
            const SizedBox(width: 8),
            Expanded(
              child: Text(
                AppConstants.disclaimer,
                style: TextStyle(
                  fontSize: 12,
                  color: textColor,
                  height: 1.4,
                ),
              ),
            ),
            if (onTap != null)
              Icon(
                Icons.chevron_right,
                color: textColor,
                size: 16,
              ),
          ],
        ),
      ),
    );
  }
}
