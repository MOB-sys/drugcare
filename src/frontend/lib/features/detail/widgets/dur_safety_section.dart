import 'package:flutter/material.dart';

import 'package:pillright/core/theme/app_colors.dart';
import 'package:pillright/features/detail/models/dur_safety_item.dart';
import 'package:pillright/features/detail/widgets/info_section.dart';

/// DUR 안전성 정보 섹션.
///
/// DUR 항목을 유형별로 그룹화하여 경고 색상과 함께 표시한다.
class DURSafetySection extends StatelessWidget {
  /// DUR 안전성 항목 목록.
  final List<DURSafetyItem> items;

  /// [DURSafetySection] 생성자.
  const DURSafetySection({super.key, required this.items});

  @override
  Widget build(BuildContext context) {
    if (items.isEmpty) {
      return const SizedBox.shrink();
    }

    // 유형별로 그룹화
    final grouped = <String, List<DURSafetyItem>>{};
    for (final item in items) {
      grouped.putIfAbsent(item.typeName, () => []).add(item);
    }

    return InfoSection(
      title: 'DUR 안전성 정보',
      icon: Icons.shield_outlined,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: grouped.entries.map((entry) {
          return _buildGroup(context, entry.key, entry.value);
        }).toList(),
      ),
    );
  }

  /// DUR 유형별 그룹을 빌드한다.
  Widget _buildGroup(
    BuildContext context,
    String typeName,
    List<DURSafetyItem> groupItems,
  ) {
    final colors = _getTypeColors(typeName);
    final isDark = Theme.of(context).brightness == Brightness.dark;

    return Container(
      margin: const EdgeInsets.only(bottom: 8),
      decoration: BoxDecoration(
        color: isDark ? colors.bgColor.withValues(alpha: 0.2) : colors.bgColor,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(
          color: colors.borderColor.withValues(alpha: isDark ? 0.4 : 0.3),
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // 유형 헤더
          Padding(
            padding: const EdgeInsets.fromLTRB(12, 10, 12, 4),
            child: Row(
              children: [
                Icon(
                  colors.icon,
                  size: 16,
                  color: colors.iconColor,
                ),
                const SizedBox(width: 6),
                Text(
                  typeName,
                  style: TextStyle(
                    fontSize: 13,
                    fontWeight: FontWeight.w600,
                    color: colors.iconColor,
                  ),
                ),
              ],
            ),
          ),
          // 각 항목
          ...groupItems.map((item) => _buildItem(context, item)),
          const SizedBox(height: 4),
        ],
      ),
    );
  }

  /// 개별 DUR 항목을 빌드한다.
  Widget _buildItem(BuildContext context, DURSafetyItem item) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final textColor =
        isDark ? AppColors.darkTextPrimary : AppColors.textPrimary;
    final subColor =
        isDark ? AppColors.darkTextSecondary : AppColors.textSecondary;

    return Padding(
      padding: const EdgeInsets.fromLTRB(12, 4, 12, 4),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          if (item.ingrName != null && item.ingrName!.isNotEmpty)
            Text(
              item.ingrName!,
              style: TextStyle(
                fontSize: 13,
                fontWeight: FontWeight.w500,
                color: textColor,
              ),
            ),
          if (item.prohibitionContent != null &&
              item.prohibitionContent!.isNotEmpty)
            Padding(
              padding: const EdgeInsets.only(top: 2),
              child: SelectableText(
                item.prohibitionContent!,
                style: TextStyle(fontSize: 12, color: subColor, height: 1.4),
              ),
            ),
          if (item.remark != null && item.remark!.isNotEmpty)
            Padding(
              padding: const EdgeInsets.only(top: 2),
              child: SelectableText(
                item.remark!,
                style: TextStyle(
                  fontSize: 11,
                  color: subColor.withValues(alpha: 0.7),
                  fontStyle: FontStyle.italic,
                  height: 1.4,
                ),
              ),
            ),
        ],
      ),
    );
  }

  /// DUR 유형에 따른 색상 세트를 반환한다.
  _DURTypeColors _getTypeColors(String typeName) {
    if (typeName.contains('임부') || typeName.contains('임산부')) {
      return const _DURTypeColors(
        bgColor: AppColors.dangerBg,
        borderColor: AppColors.danger,
        iconColor: AppColors.danger,
        icon: Icons.pregnant_woman,
      );
    }
    if (typeName.contains('노인') || typeName.contains('고령자')) {
      return const _DURTypeColors(
        bgColor: AppColors.warningBg,
        borderColor: AppColors.warning,
        iconColor: AppColors.warning,
        icon: Icons.elderly,
      );
    }
    if (typeName.contains('연령') || typeName.contains('소아')) {
      return const _DURTypeColors(
        bgColor: AppColors.cautionBg,
        borderColor: AppColors.caution,
        iconColor: AppColors.caution,
        icon: Icons.child_care,
      );
    }
    if (typeName.contains('용량')) {
      return const _DURTypeColors(
        bgColor: AppColors.warningBg,
        borderColor: AppColors.warning,
        iconColor: AppColors.warning,
        icon: Icons.speed,
      );
    }
    if (typeName.contains('투여기간')) {
      return const _DURTypeColors(
        bgColor: AppColors.infoBg,
        borderColor: AppColors.info,
        iconColor: AppColors.info,
        icon: Icons.schedule,
      );
    }
    if (typeName.contains('병용') || typeName.contains('상호작용')) {
      return const _DURTypeColors(
        bgColor: AppColors.dangerBg,
        borderColor: AppColors.danger,
        iconColor: AppColors.danger,
        icon: Icons.warning_amber_rounded,
      );
    }
    // 기본값
    return const _DURTypeColors(
      bgColor: AppColors.cautionBg,
      borderColor: AppColors.caution,
      iconColor: AppColors.caution,
      icon: Icons.info_outline,
    );
  }
}

/// DUR 유형별 색상 세트.
class _DURTypeColors {
  /// 배경 색상.
  final Color bgColor;

  /// 테두리 색상.
  final Color borderColor;

  /// 아이콘 색상.
  final Color iconColor;

  /// 아이콘.
  final IconData icon;

  /// [_DURTypeColors] 생성자.
  const _DURTypeColors({
    required this.bgColor,
    required this.borderColor,
    required this.iconColor,
    required this.icon,
  });
}
