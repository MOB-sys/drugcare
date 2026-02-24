import 'package:flutter/material.dart';

import 'package:yakmeogeo/core/theme/app_colors.dart';

/// 홈 화면 복약함 요약 카드.
///
/// 등록된 복약함 아이템 수를 보여주고, 탭하면 복약함 탭으로 이동한다.
class CabinetSummaryCard extends StatelessWidget {
  /// [CabinetSummaryCard] 생성자.
  ///
  /// [itemCount] — 복약함에 등록된 아이템 수.
  /// [onTap] — 카드 탭 시 콜백.
  const CabinetSummaryCard({
    super.key,
    required this.itemCount,
    required this.onTap,
  });

  /// 복약함 아이템 수.
  final int itemCount;

  /// 탭 시 콜백.
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return Card(
      elevation: 1,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(12),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Row(
            children: [
              Container(
                width: 48,
                height: 48,
                decoration: BoxDecoration(
                  color: AppColors.primaryLight,
                  borderRadius: BorderRadius.circular(12),
                ),
                child: const Icon(
                  Icons.medical_services_outlined,
                  color: AppColors.primaryDark,
                  size: 24,
                ),
              ),
              const SizedBox(width: 16),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text(
                      '내 복약함',
                      style: TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.w600,
                        color: AppColors.textPrimary,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      '$itemCount개 등록',
                      style: const TextStyle(
                        fontSize: 13,
                        color: AppColors.textSecondary,
                      ),
                    ),
                  ],
                ),
              ),
              const Icon(
                Icons.chevron_right,
                color: AppColors.textSecondary,
              ),
            ],
          ),
        ),
      ),
    );
  }
}
