import 'package:flutter/material.dart';

import 'package:yakmeogeo/core/theme/app_colors.dart';
import 'package:yakmeogeo/shared/models/item_type.dart';

/// 통합 검색 결과 카드 위젯.
///
/// 약물과 영양제 모두에 사용되는 검색 결과 카드.
/// 아이템 유형 태그, 이름, 선택 상태를 표시한다.
class SearchItemCard extends StatelessWidget {
  /// [SearchItemCard] 생성자.
  ///
  /// [name] — 약물/영양제 이름.
  /// [subtitle] — 부제 (제조사, 성분 등, 선택).
  /// [itemType] — 아이템 유형 (약물/영양제).
  /// [isSelected] — 선택 상태.
  /// [onTap] — 탭 콜백.
  const SearchItemCard({
    super.key,
    required this.name,
    this.subtitle,
    required this.itemType,
    required this.isSelected,
    required this.onTap,
  });

  /// 아이템 이름.
  final String name;

  /// 부제 (선택).
  final String? subtitle;

  /// 아이템 유형.
  final ItemType itemType;

  /// 선택 여부.
  final bool isSelected;

  /// 탭 콜백.
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final bool isDrug = itemType == ItemType.drug;
    final Color tagColor = isDrug ? AppColors.drugTag : AppColors.supplementTag;
    final String tagLabel = isDrug ? '약물' : '영양제';

    return Card(
      elevation: isSelected ? 2 : 0.5,
      color: isSelected ? AppColors.primaryLight.withValues(alpha: 0.3) : AppColors.surface,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(8),
        side: BorderSide(
          color: isSelected ? AppColors.primary : AppColors.divider,
          width: isSelected ? 1.5 : 0.5,
        ),
      ),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(8),
        child: Padding(
          padding: const EdgeInsets.all(12),
          child: Row(
            children: [
              // 아이템 유형 태그
              Container(
                padding: const EdgeInsets.symmetric(
                  horizontal: 8,
                  vertical: 4,
                ),
                decoration: BoxDecoration(
                  color: tagColor.withValues(alpha: 0.15),
                  borderRadius: BorderRadius.circular(4),
                ),
                child: Text(
                  tagLabel,
                  style: TextStyle(
                    fontSize: 11,
                    fontWeight: FontWeight.w600,
                    color: tagColor,
                  ),
                ),
              ),
              const SizedBox(width: 12),
              // 이름 + 부제
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      name,
                      style: const TextStyle(
                        fontSize: 15,
                        fontWeight: FontWeight.w500,
                        color: AppColors.textPrimary,
                      ),
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                    ),
                    if (subtitle != null) ...[
                      const SizedBox(height: 2),
                      Text(
                        subtitle!,
                        style: const TextStyle(
                          fontSize: 12,
                          color: AppColors.textSecondary,
                        ),
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                      ),
                    ],
                  ],
                ),
              ),
              // 선택 상태 체크마크
              Icon(
                isSelected
                    ? Icons.check_circle
                    : Icons.radio_button_unchecked,
                color: isSelected ? AppColors.primary : AppColors.textDisabled,
                size: 24,
              ),
            ],
          ),
        ),
      ),
    );
  }
}
