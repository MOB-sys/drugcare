import 'package:flutter/material.dart';

import 'package:pillright/core/theme/app_colors.dart';
import 'package:pillright/features/detail/widgets/info_section.dart';
import 'package:pillright/shared/models/ingredient_info.dart';

/// 약물 성분 테이블 위젯.
///
/// [IngredientInfo] 목록을 성분명·함량·단위 테이블로 표시한다.
class IngredientsTable extends StatelessWidget {
  /// 성분 목록.
  final List<IngredientInfo> ingredients;

  /// [IngredientsTable] 생성자.
  const IngredientsTable({super.key, required this.ingredients});

  @override
  Widget build(BuildContext context) {
    if (ingredients.isEmpty) {
      return const SizedBox.shrink();
    }

    return InfoSection(
      title: '성분 정보',
      icon: Icons.science_outlined,
      child: _buildTable(context),
    );
  }

  /// 성분 테이블을 빌드한다.
  Widget _buildTable(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final headerBg = isDark ? AppColors.darkSurface : AppColors.primaryLight;
    final headerText = isDark ? AppColors.darkTextPrimary : AppColors.primary;
    final borderColor = isDark ? AppColors.darkDivider : AppColors.divider;

    return Container(
      decoration: BoxDecoration(
        border: Border.all(color: borderColor),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Column(
        children: [
          // 헤더
          Container(
            decoration: BoxDecoration(
              color: headerBg,
              borderRadius: const BorderRadius.vertical(
                top: Radius.circular(7),
              ),
            ),
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
            child: Row(
              children: [
                Expanded(
                  flex: 3,
                  child: Text(
                    '성분명',
                    style: TextStyle(
                      fontSize: 13,
                      fontWeight: FontWeight.w600,
                      color: headerText,
                    ),
                  ),
                ),
                Expanded(
                  flex: 2,
                  child: Text(
                    '함량',
                    textAlign: TextAlign.end,
                    style: TextStyle(
                      fontSize: 13,
                      fontWeight: FontWeight.w600,
                      color: headerText,
                    ),
                  ),
                ),
              ],
            ),
          ),
          // 행
          ...ingredients.asMap().entries.map((entry) {
            final index = entry.key;
            final item = entry.value;
            final isLast = index == ingredients.length - 1;
            final rowBg = index.isEven
                ? Colors.transparent
                : (isDark
                    ? AppColors.darkSurfaceHover.withValues(alpha: 0.3)
                    : AppColors.surfaceHover);

            return Container(
              decoration: BoxDecoration(
                color: rowBg,
                border: isLast
                    ? null
                    : Border(bottom: BorderSide(color: borderColor, width: 0.5)),
                borderRadius: isLast
                    ? const BorderRadius.vertical(bottom: Radius.circular(7))
                    : null,
              ),
              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
              child: Row(
                children: [
                  Expanded(
                    flex: 3,
                    child: Text(
                      item.name,
                      style: const TextStyle(fontSize: 13),
                    ),
                  ),
                  Expanded(
                    flex: 2,
                    child: Text(
                      _formatAmount(item),
                      textAlign: TextAlign.end,
                      style: TextStyle(
                        fontSize: 13,
                        color: isDark
                            ? AppColors.darkTextSecondary
                            : AppColors.textSecondary,
                      ),
                    ),
                  ),
                ],
              ),
            );
          }),
        ],
      ),
    );
  }

  /// 함량과 단위를 포맷팅한다.
  String _formatAmount(IngredientInfo item) {
    final amount = item.amount ?? '';
    final unit = item.unit ?? '';
    if (amount.isEmpty && unit.isEmpty) return '-';
    return '$amount $unit'.trim();
  }
}

/// 영양제 성분 테이블 위젯.
///
/// 원본 JSON 구조의 성분 목록을 테이블로 표시한다.
class SupplementIngredientsTable extends StatelessWidget {
  /// 성분 목록 (원본 JSON 맵).
  final List<Map<String, dynamic>> ingredients;

  /// [SupplementIngredientsTable] 생성자.
  const SupplementIngredientsTable({super.key, required this.ingredients});

  @override
  Widget build(BuildContext context) {
    if (ingredients.isEmpty) {
      return const SizedBox.shrink();
    }

    return InfoSection(
      title: '성분 정보',
      icon: Icons.science_outlined,
      child: _buildTable(context),
    );
  }

  /// 성분 테이블을 빌드한다.
  Widget _buildTable(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final headerBg = isDark ? AppColors.darkSurface : AppColors.primaryLight;
    final headerText = isDark ? AppColors.darkTextPrimary : AppColors.primary;
    final borderColor = isDark ? AppColors.darkDivider : AppColors.divider;

    return Container(
      decoration: BoxDecoration(
        border: Border.all(color: borderColor),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Column(
        children: [
          // 헤더
          Container(
            decoration: BoxDecoration(
              color: headerBg,
              borderRadius: const BorderRadius.vertical(
                top: Radius.circular(7),
              ),
            ),
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
            child: Row(
              children: [
                Expanded(
                  flex: 3,
                  child: Text(
                    '성분명',
                    style: TextStyle(
                      fontSize: 13,
                      fontWeight: FontWeight.w600,
                      color: headerText,
                    ),
                  ),
                ),
                Expanded(
                  flex: 2,
                  child: Text(
                    '함량',
                    textAlign: TextAlign.end,
                    style: TextStyle(
                      fontSize: 13,
                      fontWeight: FontWeight.w600,
                      color: headerText,
                    ),
                  ),
                ),
              ],
            ),
          ),
          // 행
          ...ingredients.asMap().entries.map((entry) {
            final index = entry.key;
            final item = entry.value;
            final isLast = index == ingredients.length - 1;
            final rowBg = index.isEven
                ? Colors.transparent
                : (isDark
                    ? AppColors.darkSurfaceHover.withValues(alpha: 0.3)
                    : AppColors.surfaceHover);

            final name = (item['name'] ?? item['ingredient_name'] ?? '-')
                .toString();
            final amount = (item['amount'] ?? item['quantity'] ?? '')
                .toString();
            final unit = (item['unit'] ?? '').toString();
            final display =
                amount.isEmpty && unit.isEmpty ? '-' : '$amount $unit'.trim();

            return Container(
              decoration: BoxDecoration(
                color: rowBg,
                border: isLast
                    ? null
                    : Border(bottom: BorderSide(color: borderColor, width: 0.5)),
                borderRadius: isLast
                    ? const BorderRadius.vertical(bottom: Radius.circular(7))
                    : null,
              ),
              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
              child: Row(
                children: [
                  Expanded(
                    flex: 3,
                    child: Text(name, style: const TextStyle(fontSize: 13)),
                  ),
                  Expanded(
                    flex: 2,
                    child: Text(
                      display,
                      textAlign: TextAlign.end,
                      style: TextStyle(
                        fontSize: 13,
                        color: isDark
                            ? AppColors.darkTextSecondary
                            : AppColors.textSecondary,
                      ),
                    ),
                  ),
                ],
              ),
            );
          }),
        ],
      ),
    );
  }
}
