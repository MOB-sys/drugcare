import 'package:flutter/material.dart';

import 'package:pillright/core/theme/app_colors.dart';
import 'package:pillright/features/detail/models/dur_safety_item.dart';
import 'package:pillright/features/detail/widgets/info_section.dart';

/// 임신·수유 안전정보 섹션.
///
/// DUR 임부금기 데이터와 주의사항 텍스트에서 임신/수유 관련 내용을
/// 추출하여 구조화된 경고 컨테이너로 표시한다.
class PregnancySafetySection extends StatelessWidget {
  /// DUR 안전성 항목 중 임부 관련 항목.
  final List<DURSafetyItem> pregnancyItems;

  /// 수유 관련 문장 목록.
  final List<String> breastfeedingSentences;

  /// 임부/임산부/임신 관련 주의 문장 목록.
  final List<String> pregnancyCautionSentences;

  /// [PregnancySafetySection] 생성자.
  const PregnancySafetySection({
    super.key,
    required this.pregnancyItems,
    required this.breastfeedingSentences,
    required this.pregnancyCautionSentences,
  });

  /// 주어진 데이터로부터 표시할 내용이 있는지 확인한다.
  static bool shouldShow({
    List<DURSafetyItem>? durSafety,
    String? atpnQesitm,
    String? atpnWarnQesitm,
  }) {
    // DUR에 pregnancy 항목이 있는지 확인
    final hasPregnancyDur = durSafety?.any(
          (item) => item.durType == 'pregnancy',
        ) ??
        false;
    if (hasPregnancyDur) return true;

    // 주의사항에 키워드가 있는지 확인
    const keywords = ['임부', '임산부', '임신', '수유'];
    final texts = [
      if (atpnQesitm != null) atpnQesitm,
      if (atpnWarnQesitm != null) atpnWarnQesitm,
    ].join(' ');

    return keywords.any((kw) => texts.contains(kw));
  }

  /// DrugDetail 데이터에서 PregnancySafetySection 위젯 데이터를 추출한다.
  static PregnancySafetyData extractData({
    List<DURSafetyItem>? durSafety,
    String? atpnQesitm,
    String? atpnWarnQesitm,
  }) {
    // 1. DUR 임부 금기 항목
    final pregnancyItems = durSafety
            ?.where((item) => item.durType == 'pregnancy')
            .toList() ??
        [];

    // 2. 수유 관련 문장 추출
    final breastfeedingSentences = <String>[];
    for (final text in [atpnQesitm, atpnWarnQesitm]) {
      if (text == null || text.trim().isEmpty) continue;
      final sentences = _splitSentences(text);
      for (final s in sentences) {
        if (s.contains('수유')) {
          breastfeedingSentences.add(s.trim());
        }
      }
    }

    // 3. 임부/임산부/임신 관련 문장 (수유 문장 제외)
    final pregnancyCautionSentences = <String>[];
    const pregnancyKeywords = ['임부', '임산부', '임신'];
    for (final text in [atpnQesitm, atpnWarnQesitm]) {
      if (text == null || text.trim().isEmpty) continue;
      final sentences = _splitSentences(text);
      for (final s in sentences) {
        final trimmed = s.trim();
        if (trimmed.isEmpty) continue;
        // 이미 수유 문장으로 포함된 것은 제외
        if (breastfeedingSentences.contains(trimmed)) continue;
        if (pregnancyKeywords.any((kw) => trimmed.contains(kw))) {
          pregnancyCautionSentences.add(trimmed);
        }
      }
    }

    return PregnancySafetyData(
      pregnancyItems: pregnancyItems,
      breastfeedingSentences: breastfeedingSentences,
      pregnancyCautionSentences: pregnancyCautionSentences,
    );
  }

  /// 텍스트를 문장 단위로 분리한다.
  static List<String> _splitSentences(String text) {
    // 마침표, 줄바꿈 기준으로 분리
    return text
        .split(RegExp(r'[.\n]'))
        .map((s) => s.trim())
        .where((s) => s.isNotEmpty)
        .toList();
  }

  @override
  Widget build(BuildContext context) {
    final hasContent = pregnancyItems.isNotEmpty ||
        breastfeedingSentences.isNotEmpty ||
        pregnancyCautionSentences.isNotEmpty;

    if (!hasContent) return const SizedBox.shrink();

    return InfoSection(
      title: '임신·수유 안전정보',
      icon: Icons.pregnant_woman,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // 임부 금기 (DUR)
          if (pregnancyItems.isNotEmpty)
            _buildWarningContainer(
              context,
              label: '임부 금기',
              icon: Icons.dangerous_outlined,
              bgColor: AppColors.dangerBg,
              borderColor: AppColors.danger,
              labelColor: AppColors.danger,
              children: pregnancyItems
                  .map((item) => _buildDurItem(context, item))
                  .toList(),
            ),

          // 수유부 주의
          if (breastfeedingSentences.isNotEmpty)
            _buildWarningContainer(
              context,
              label: '수유부 주의',
              icon: Icons.warning_amber_rounded,
              bgColor: AppColors.warningBg,
              borderColor: AppColors.warning,
              labelColor: AppColors.warning,
              children: breastfeedingSentences
                  .map((s) => _buildSentenceItem(context, s))
                  .toList(),
            ),

          // 관련 주의사항
          if (pregnancyCautionSentences.isNotEmpty)
            _buildWarningContainer(
              context,
              label: '관련 주의사항',
              icon: Icons.info_outline,
              bgColor: AppColors.cautionBg,
              borderColor: AppColors.caution,
              labelColor: AppColors.caution,
              children: pregnancyCautionSentences
                  .map((s) => _buildSentenceItem(context, s))
                  .toList(),
            ),
        ],
      ),
    );
  }

  /// 경고 컨테이너를 빌드한다.
  Widget _buildWarningContainer(
    BuildContext context, {
    required String label,
    required IconData icon,
    required Color bgColor,
    required Color borderColor,
    required Color labelColor,
    required List<Widget> children,
  }) {
    final isDark = Theme.of(context).brightness == Brightness.dark;

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
          ...children,
          const SizedBox(height: 4),
        ],
      ),
    );
  }

  /// DUR 항목을 빌드한다.
  Widget _buildDurItem(BuildContext context, DURSafetyItem item) {
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

  /// 문장 항목을 빌드한다.
  Widget _buildSentenceItem(BuildContext context, String sentence) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final textColor =
        isDark ? AppColors.darkTextPrimary : AppColors.textPrimary;

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
}

/// 임신·수유 안전정보 추출 데이터.
class PregnancySafetyData {
  /// DUR 임부 금기 항목.
  final List<DURSafetyItem> pregnancyItems;

  /// 수유 관련 문장 목록.
  final List<String> breastfeedingSentences;

  /// 임부/임산부/임신 관련 주의 문장 목록.
  final List<String> pregnancyCautionSentences;

  /// [PregnancySafetyData] 생성자.
  const PregnancySafetyData({
    required this.pregnancyItems,
    required this.breastfeedingSentences,
    required this.pregnancyCautionSentences,
  });

  /// 표시할 내용이 있는지 여부.
  bool get hasContent =>
      pregnancyItems.isNotEmpty ||
      breastfeedingSentences.isNotEmpty ||
      pregnancyCautionSentences.isNotEmpty;
}
