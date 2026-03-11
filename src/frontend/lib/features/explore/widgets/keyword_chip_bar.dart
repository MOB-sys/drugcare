import 'package:flutter/material.dart';

import 'package:pillright/core/theme/app_colors.dart';

/// 키워드 칩 바 — 가로 스크롤 키워드 선택 (복수 선택 지원).
///
/// 자주 찾는 증상·부작용 등의 키워드를 가로 스크롤로 표시하며,
/// 선택 시 [onSelected] 콜백을 호출한다.
/// [selectedKeywords]로 복수 선택을, [selected]로 단일 선택을 지원한다.
class KeywordChipBar extends StatelessWidget {
  /// [KeywordChipBar] 생성자.
  const KeywordChipBar({
    super.key,
    required this.keywords,
    @Deprecated('Use selectedKeywords instead') this.selected,
    this.selectedKeywords = const [],
    required this.onSelected,
  });

  /// 키워드 목록.
  final List<String> keywords;

  /// 현재 선택된 키워드 (단일 — 하위 호환용).
  final String? selected;

  /// 현재 선택된 키워드 목록 (복수 선택).
  final List<String> selectedKeywords;

  /// 키워드 선택 콜백.
  final ValueChanged<String> onSelected;

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      scrollDirection: Axis.horizontal,
      padding: const EdgeInsets.symmetric(horizontal: 16),
      child: Row(
        children: keywords.map((keyword) {
          final isSelected = selectedKeywords.contains(keyword) ||
              keyword == selected;
          return Padding(
            padding: const EdgeInsets.only(right: 8),
            child: ChoiceChip(
              label: Text(keyword),
              selected: isSelected,
              onSelected: (_) => onSelected(keyword),
              selectedColor: AppColors.primary,
              backgroundColor: AppColors.surface,
              side: BorderSide(
                color: isSelected ? AppColors.primary : AppColors.divider,
              ),
              labelStyle: TextStyle(
                color: isSelected ? Colors.white : AppColors.textPrimary,
                fontSize: 13,
              ),
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(20),
              ),
            ),
          );
        }).toList(),
      ),
    );
  }
}
