import 'package:flutter/material.dart';

import 'package:yakmeogeo/core/constants/app_constants.dart';

/// 의료 면책조항 배너 위젯.
///
/// 모든 결과 화면 하단에 표시되는 노란색/앰버 경고 배너.
/// 탭하면 상세 면책조항을 보여줄 수 있다.
class DisclaimerBanner extends StatelessWidget {
  /// [DisclaimerBanner] 생성자.
  ///
  /// [onTap] — 배너 탭 시 상세 면책조항 표시 콜백 (선택).
  const DisclaimerBanner({super.key, this.onTap});

  /// 배너 탭 시 콜백.
  final VoidCallback? onTap;

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        width: double.infinity,
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
        decoration: BoxDecoration(
          color: const Color(0xFFFFF8E1),
          borderRadius: BorderRadius.circular(8),
          border: Border.all(color: const Color(0xFFFFE082)),
        ),
        child: Row(
          children: [
            const Icon(
              Icons.warning_amber_rounded,
              color: Color(0xFFF9A825),
              size: 20,
            ),
            const SizedBox(width: 8),
            const Expanded(
              child: Text(
                AppConstants.disclaimer,
                style: TextStyle(
                  fontSize: 12,
                  color: Color(0xFF5D4037),
                  height: 1.4,
                ),
              ),
            ),
            if (onTap != null)
              const Icon(
                Icons.chevron_right,
                color: Color(0xFF5D4037),
                size: 16,
              ),
          ],
        ),
      ),
    );
  }
}
