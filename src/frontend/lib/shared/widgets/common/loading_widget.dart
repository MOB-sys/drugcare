import 'package:flutter/material.dart';

import 'package:yakmeogeo/core/theme/app_colors.dart';

/// 로딩 인디케이터 위젯.
///
/// 중앙 정렬된 [CircularProgressIndicator]와 선택적 메시지 텍스트.
class LoadingWidget extends StatelessWidget {
  /// [LoadingWidget] 생성자.
  ///
  /// [message] — 로딩 중 표시할 텍스트 (선택).
  const LoadingWidget({super.key, this.message});

  /// 로딩 메시지.
  final String? message;

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          const CircularProgressIndicator(color: AppColors.primary),
          if (message != null) ...[
            const SizedBox(height: 16),
            Text(
              message!,
              style: const TextStyle(
                fontSize: 14,
                color: AppColors.textSecondary,
              ),
              textAlign: TextAlign.center,
            ),
          ],
        ],
      ),
    );
  }
}
