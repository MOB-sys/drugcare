import 'package:flutter/material.dart';

import 'package:pillright/core/theme/app_colors.dart';

/// 상세 화면 하단 CTA 버튼 영역.
///
/// '상호작용 체크하기'와 '복약함에 추가' 버튼을 가로로 배치한다.
class DetailCtaButtons extends StatelessWidget {
  /// 상호작용 체크 버튼 콜백.
  final VoidCallback? onCheckInteraction;

  /// 복약함 추가 버튼 콜백.
  final VoidCallback? onAddToCabinet;

  /// 복약함 추가 로딩 상태.
  final bool isAddingToCabinet;

  /// [DetailCtaButtons] 생성자.
  const DetailCtaButtons({
    super.key,
    this.onCheckInteraction,
    this.onAddToCabinet,
    this.isAddingToCabinet = false,
  });

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Row(
        children: [
          // 상호작용 체크 버튼
          Expanded(
            child: FilledButton.icon(
              onPressed: onCheckInteraction,
              icon: const Icon(Icons.compare_arrows, size: 18),
              label: const Text('상호작용 체크'),
              style: FilledButton.styleFrom(
                backgroundColor: AppColors.accent,
                foregroundColor: Colors.white,
                padding: const EdgeInsets.symmetric(vertical: 14),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(12),
                ),
              ),
            ),
          ),
          const SizedBox(width: 12),
          // 복약함에 추가 버튼
          Expanded(
            child: OutlinedButton.icon(
              onPressed: isAddingToCabinet ? null : onAddToCabinet,
              icon: isAddingToCabinet
                  ? const SizedBox(
                      width: 16,
                      height: 16,
                      child: CircularProgressIndicator(strokeWidth: 2),
                    )
                  : const Icon(Icons.add_box_outlined, size: 18),
              label: Text(
                isAddingToCabinet ? '추가 중...' : '복약함에 추가',
              ),
              style: OutlinedButton.styleFrom(
                foregroundColor: AppColors.primary,
                padding: const EdgeInsets.symmetric(vertical: 14),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(12),
                ),
                side: const BorderSide(color: AppColors.primary),
              ),
            ),
          ),
        ],
      ),
    );
  }
}
