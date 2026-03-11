import 'package:flutter/material.dart';

import 'package:pillright/core/theme/app_colors.dart';
import 'package:pillright/features/detail/widgets/info_section.dart';

/// 구조화된 부작용 정보 섹션.
///
/// 부작용 텍스트를 심각/일반/기타로 분류하여 색상 구분된 컨테이너로
/// 표시하고, 부작용 대처 안내를 하단에 추가한다.
class StructuredSideEffects extends StatelessWidget {
  /// 부작용 원본 텍스트.
  final String sideEffectsText;

  /// [StructuredSideEffects] 생성자.
  const StructuredSideEffects({
    super.key,
    required this.sideEffectsText,
  });

  /// 심각한 부작용 키워드.
  static const _seriousKeywords = [
    '즉시 중단',
    '의사',
    '응급',
    '심각',
    '사망',
    '아나필락시스',
    '호흡곤란',
    '쇼크',
    '중증',
  ];

  /// 일반 부작용 키워드.
  static const _commonKeywords = [
    '흔히',
    '흔하',
    '자주',
    '일반적',
    '때때로',
    '가끔',
  ];

  @override
  Widget build(BuildContext context) {
    final text = sideEffectsText.trim();
    if (text.isEmpty) return const SizedBox.shrink();

    final sentences = _splitSentences(text);

    // 2문장 이하면 분류하지 않고 그대로 표시
    if (sentences.length <= 2) {
      return _buildSimpleView(context, text);
    }

    return _buildCategorizedView(context, sentences);
  }

  /// 짧은 텍스트를 분류 없이 표시한다.
  Widget _buildSimpleView(BuildContext context, String text) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final textColor =
        isDark ? AppColors.darkTextPrimary : AppColors.textPrimary;

    return InfoSection(
      title: '부작용',
      icon: Icons.report_problem_outlined,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SelectableText(
            text,
            style: TextStyle(fontSize: 14, height: 1.6, color: textColor),
          ),
          const SizedBox(height: 12),
          _buildGuidanceBox(context),
        ],
      ),
    );
  }

  /// 분류된 부작용을 표시한다.
  Widget _buildCategorizedView(
    BuildContext context,
    List<String> sentences,
  ) {
    final serious = <String>[];
    final common = <String>[];
    final other = <String>[];

    for (final s in sentences) {
      if (_seriousKeywords.any((kw) => s.contains(kw))) {
        serious.add(s);
      } else if (_commonKeywords.any((kw) => s.contains(kw))) {
        common.add(s);
      } else {
        other.add(s);
      }
    }

    return InfoSection(
      title: '부작용',
      icon: Icons.report_problem_outlined,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          if (serious.isNotEmpty)
            _buildCategoryContainer(
              context,
              label: '심각한 부작용',
              icon: Icons.error_outline,
              bgColor: AppColors.dangerBg,
              borderColor: AppColors.danger,
              labelColor: AppColors.danger,
              sentences: serious,
            ),
          if (common.isNotEmpty)
            _buildCategoryContainer(
              context,
              label: '일반적 부작용',
              icon: Icons.warning_amber_rounded,
              bgColor: AppColors.cautionBg,
              borderColor: AppColors.caution,
              labelColor: AppColors.caution,
              sentences: common,
            ),
          if (other.isNotEmpty)
            _buildCategoryContainer(
              context,
              label: '기타 부작용',
              icon: Icons.info_outline,
              bgColor: AppColors.infoBg,
              borderColor: AppColors.info,
              labelColor: AppColors.info,
              sentences: other,
            ),
          const SizedBox(height: 4),
          _buildGuidanceBox(context),
        ],
      ),
    );
  }

  /// 부작용 카테고리 컨테이너를 빌드한다.
  Widget _buildCategoryContainer(
    BuildContext context, {
    required String label,
    required IconData icon,
    required Color bgColor,
    required Color borderColor,
    required Color labelColor,
    required List<String> sentences,
  }) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final textColor =
        isDark ? AppColors.darkTextPrimary : AppColors.textPrimary;

    return Container(
      width: double.infinity,
      margin: const EdgeInsets.only(bottom: 8),
      decoration: BoxDecoration(
        color: isDark ? bgColor.withValues(alpha: 0.2) : bgColor,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(
          color: borderColor.withValues(alpha: isDark ? 0.4 : 0.3),
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // 헤더
          Padding(
            padding: const EdgeInsets.fromLTRB(12, 10, 12, 4),
            child: Row(
              children: [
                Icon(icon, size: 16, color: labelColor),
                const SizedBox(width: 6),
                Text(
                  label,
                  style: TextStyle(
                    fontSize: 13,
                    fontWeight: FontWeight.w600,
                    color: labelColor,
                  ),
                ),
              ],
            ),
          ),
          // 문장 목록
          ...sentences.map((s) => _buildSentenceItem(context, s, textColor)),
          const SizedBox(height: 4),
        ],
      ),
    );
  }

  /// 문장 항목을 빌드한다.
  Widget _buildSentenceItem(
    BuildContext context,
    String sentence,
    Color textColor,
  ) {
    return Padding(
      padding: const EdgeInsets.fromLTRB(12, 4, 12, 4),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Padding(
            padding: const EdgeInsets.only(top: 4),
            child: Icon(
              Icons.circle,
              size: 5,
              color: textColor.withValues(alpha: 0.5),
            ),
          ),
          const SizedBox(width: 8),
          Expanded(
            child: SelectableText(
              sentence,
              style: TextStyle(fontSize: 12, color: textColor, height: 1.4),
            ),
          ),
        ],
      ),
    );
  }

  /// 부작용 대처 안내 박스를 빌드한다.
  Widget _buildGuidanceBox(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;

    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: isDark
            ? AppColors.safeBg.withValues(alpha: 0.15)
            : AppColors.safeBg,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(
          color: AppColors.safe.withValues(alpha: isDark ? 0.3 : 0.2),
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Row(
            children: [
              Icon(Icons.medical_services_outlined,
                  size: 16, color: AppColors.safe),
              SizedBox(width: 6),
              Text(
                '부작용 대처',
                style: TextStyle(
                  fontSize: 13,
                  fontWeight: FontWeight.w600,
                  color: AppColors.safe,
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),
          _buildGuidanceItem(
            context,
            '부작용이 나타나면 즉시 의사 또는 약사에게 알리십시오.',
          ),
          const SizedBox(height: 4),
          _buildGuidanceItem(
            context,
            '약 복용을 임의로 중단하지 마십시오.',
          ),
        ],
      ),
    );
  }

  /// 대처 안내 항목을 빌드한다.
  Widget _buildGuidanceItem(BuildContext context, String text) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final textColor =
        isDark ? AppColors.darkTextPrimary : AppColors.textPrimary;

    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Padding(
          padding: EdgeInsets.only(top: 2),
          child: Icon(Icons.check_circle_outline,
              size: 14, color: AppColors.safe),
        ),
        const SizedBox(width: 6),
        Expanded(
          child: Text(
            text,
            style: TextStyle(fontSize: 12, color: textColor, height: 1.4),
          ),
        ),
      ],
    );
  }

  /// 텍스트를 문장 단위로 분리한다.
  List<String> _splitSentences(String text) {
    return text
        .split(RegExp(r'[.\n]'))
        .map((s) => s.trim())
        .where((s) => s.isNotEmpty)
        .toList();
  }
}
