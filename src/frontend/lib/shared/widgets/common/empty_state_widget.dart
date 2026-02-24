import 'package:flutter/material.dart';

import 'package:yakmeogeo/core/theme/app_colors.dart';

/// 빈 상태 플레이스홀더 위젯.
///
/// 데이터가 없을 때 아이콘과 안내 메시지를 중앙에 표시한다.
class EmptyStateWidget extends StatelessWidget {
  /// [EmptyStateWidget] 생성자.
  ///
  /// [message] — 표시할 안내 메시지.
  /// [icon] — 표시할 아이콘 (기본: [Icons.inbox_outlined]).
  const EmptyStateWidget({
    super.key,
    required this.message,
    this.icon = Icons.inbox_outlined,
  });

  /// 안내 메시지.
  final String message;

  /// 표시 아이콘.
  final IconData icon;

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 32),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(icon, size: 64, color: AppColors.textDisabled),
            const SizedBox(height: 16),
            Text(
              message,
              style: const TextStyle(
                fontSize: 14,
                color: AppColors.textSecondary,
              ),
              textAlign: TextAlign.center,
            ),
          ],
        ),
      ),
    );
  }
}
