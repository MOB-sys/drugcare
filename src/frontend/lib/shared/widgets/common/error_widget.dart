import 'package:flutter/material.dart';

import 'package:yakmeogeo/core/theme/app_colors.dart';

/// 에러 상태 표시 위젯.
///
/// 에러 아이콘, 메시지, "다시 시도" 버튼을 중앙에 표시한다.
/// Flutter 내장 [ErrorWidget]과 이름 충돌을 피하기 위해 [AppErrorWidget]으로 명명.
class AppErrorWidget extends StatelessWidget {
  /// [AppErrorWidget] 생성자.
  ///
  /// [message] — 표시할 에러 메시지.
  /// [onRetry] — 재시도 버튼 콜백 (선택, null이면 버튼 숨김).
  const AppErrorWidget({
    super.key,
    required this.message,
    this.onRetry,
  });

  /// 에러 메시지.
  final String message;

  /// 재시도 콜백.
  final VoidCallback? onRetry;

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 32),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Icon(
              Icons.error_outline,
              size: 48,
              color: AppColors.danger,
            ),
            const SizedBox(height: 16),
            Text(
              message,
              style: const TextStyle(
                fontSize: 14,
                color: AppColors.textSecondary,
              ),
              textAlign: TextAlign.center,
            ),
            if (onRetry != null) ...[
              const SizedBox(height: 20),
              ElevatedButton(
                onPressed: onRetry,
                style: ElevatedButton.styleFrom(
                  backgroundColor: AppColors.primary,
                  foregroundColor: Colors.white,
                  minimumSize: const Size(48, 48),
                ),
                child: const Text('다시 시도'),
              ),
            ],
          ],
        ),
      ),
    );
  }
}
