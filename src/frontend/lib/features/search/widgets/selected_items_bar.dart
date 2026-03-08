import 'package:flutter/material.dart';

import 'package:pillright/core/theme/app_colors.dart';
import 'package:pillright/features/search/models/selected_search_item.dart';
import 'package:pillright/shared/models/item_type.dart';

/// 선택된 아이템 가로 스크롤 칩 바.
///
/// 선택된 약물/영양제를 칩 형태로 표시하며, 삭제 아이콘으로 선택 해제할 수 있다.
class SelectedItemsBar extends StatelessWidget {
  /// [SelectedItemsBar] 생성자.
  ///
  /// [selectedItems] — 선택된 아이템 목록.
  /// [onDelete] — 개별 아이템 삭제 콜백.
  /// [onClear] — 전체 선택 해제 콜백.
  const SelectedItemsBar({
    super.key,
    required this.selectedItems,
    required this.onDelete,
    required this.onClear,
  });

  /// 선택된 아이템 목록.
  final List<SelectedSearchItem> selectedItems;

  /// 개별 아이템 삭제 콜백.
  final ValueChanged<SelectedSearchItem> onDelete;

  /// 전체 선택 해제 콜백.
  final VoidCallback onClear;

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
      decoration: const BoxDecoration(
        color: AppColors.surface,
        border: Border(
          top: BorderSide(color: AppColors.divider, width: 0.5),
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisSize: MainAxisSize.min,
        children: [
          // 선택 수 + 초기화
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                '${selectedItems.length}개 선택됨',
                style: const TextStyle(
                  fontSize: 13,
                  fontWeight: FontWeight.w600,
                  color: AppColors.textPrimary,
                ),
              ),
              GestureDetector(
                onTap: onClear,
                child: const Text(
                  '초기화',
                  style: TextStyle(
                    fontSize: 12,
                    color: AppColors.textSecondary,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 6),
          // 칩 목록
          SingleChildScrollView(
            scrollDirection: Axis.horizontal,
            child: Row(
              children: selectedItems.map((item) {
                final isDrug = item.itemType == ItemType.drug;
                final tagColor =
                    isDrug ? AppColors.drugTag : AppColors.supplementTag;
                return Padding(
                  padding: const EdgeInsets.only(right: 6),
                  child: Chip(
                    label: Text(
                      item.name,
                      style: TextStyle(fontSize: 12, color: tagColor),
                    ),
                    deleteIcon: Icon(Icons.close, size: 16, color: tagColor),
                    onDeleted: () => onDelete(item),
                    backgroundColor: tagColor.withValues(alpha: 0.1),
                    side: BorderSide(color: tagColor.withValues(alpha: 0.3)),
                    materialTapTargetSize: MaterialTapTargetSize.shrinkWrap,
                    visualDensity: VisualDensity.compact,
                  ),
                );
              }).toList(),
            ),
          ),
        ],
      ),
    );
  }
}
