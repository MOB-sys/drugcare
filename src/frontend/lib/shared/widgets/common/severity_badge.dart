import 'package:flutter/material.dart';

import 'package:pillright/shared/models/severity.dart';

/// 상호작용 심각도 배지 위젯.
///
/// 신호등 시스템에 따라 색상·아이콘·라벨을 표시하는 칩 형태 배지.
class SeverityBadge extends StatelessWidget {
  /// [SeverityBadge] 생성자.
  ///
  /// [severity] — 표시할 심각도 레벨.
  const SeverityBadge({super.key, required this.severity});

  /// 심각도 열거형.
  final Severity severity;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: severity.backgroundColor,
        borderRadius: BorderRadius.circular(12),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(severity.icon, size: 14, color: severity.color),
          const SizedBox(width: 4),
          Text(
            severity.label,
            style: TextStyle(
              fontSize: 12,
              fontWeight: FontWeight.w600,
              color: severity.color,
            ),
          ),
        ],
      ),
    );
  }
}
