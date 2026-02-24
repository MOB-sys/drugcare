import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import 'package:yakmeogeo/core/theme/app_colors.dart';

/// 홈 화면 퀵 검색 바.
///
/// 실제 입력은 불가하며, 탭하면 검색 화면(/search)으로 이동한다.
class QuickSearchBar extends StatelessWidget {
  /// [QuickSearchBar] 생성자.
  const QuickSearchBar({super.key});

  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: () => context.push('/search'),
      borderRadius: BorderRadius.circular(12),
      child: Container(
        height: 48,
        padding: const EdgeInsets.symmetric(horizontal: 16),
        decoration: BoxDecoration(
          color: AppColors.surface,
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: AppColors.divider),
        ),
        child: const Row(
          children: [
            Icon(Icons.search, color: AppColors.textSecondary),
            SizedBox(width: 12),
            Expanded(
              child: Text(
                '약물 또는 영양제를 검색하세요',
                style: TextStyle(
                  fontSize: 15,
                  color: AppColors.textDisabled,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
