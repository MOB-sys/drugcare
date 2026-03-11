import 'package:flutter/material.dart';

import 'package:pillright/core/theme/app_colors.dart';
import 'package:pillright/features/cabinet/models/cabinet_item.dart';
import 'package:pillright/shared/models/item_type.dart';

/// 복약함 개별 아이템 타일.
///
/// 아이템 이름, 별칭, 유형 뱃지를 표시하고 삭제 버튼을 제공한다.
class CabinetItemTile extends StatelessWidget {
  /// [CabinetItemTile] 생성자.
  ///
  /// [item] — 표시할 복약함 아이템.
  /// [onDelete] — 삭제 버튼 콜백.
  const CabinetItemTile({
    super.key,
    required this.item,
    required this.onDelete,
  });

  /// 복약함 아이템.
  final CabinetItem item;

  /// 삭제 콜백.
  final VoidCallback onDelete;

  @override
  Widget build(BuildContext context) {
    final Color tagColor;
    final String tagLabel;
    switch (item.itemType) {
      case ItemType.drug:
        tagColor = AppColors.drugTag;
        tagLabel = '약물';
      case ItemType.supplement:
        tagColor = AppColors.supplementTag;
        tagLabel = '영양제';
      case ItemType.food:
        tagColor = AppColors.foodTag;
        tagLabel = '식품';
      case ItemType.herbal:
        tagColor = AppColors.herbalTag;
        tagLabel = '한약재';
    }

    return Card(
      elevation: 0.5,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
        child: Row(
          children: [
            // 유형 뱃지
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
              decoration: BoxDecoration(
                color: tagColor.withValues(alpha: 0.15),
                borderRadius: BorderRadius.circular(6),
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

            // 이름 + 별칭
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    item.itemName,
                    style: const TextStyle(
                      fontSize: 15,
                      fontWeight: FontWeight.w600,
                      color: AppColors.textPrimary,
                    ),
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                  ),
                  if (item.nickname != null && item.nickname!.isNotEmpty) ...[
                    const SizedBox(height: 2),
                    Text(
                      item.nickname!,
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

            // 삭제 버튼
            IconButton(
              onPressed: onDelete,
              icon: const Icon(Icons.delete_outline),
              color: AppColors.textSecondary,
              iconSize: 20,
              constraints: const BoxConstraints(minWidth: 48, minHeight: 48),
              tooltip: '삭제',
            ),
          ],
        ),
      ),
    );
  }
}
