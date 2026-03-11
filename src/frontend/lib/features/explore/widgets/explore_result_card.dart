import 'package:flutter/material.dart';

import 'package:pillright/core/theme/app_colors.dart';

/// 탐색 결과 카드.
///
/// 증상·부작용·질환별 검색 결과를 통일된 형태로 표시한다.
/// [highlightKeyword]가 지정되면 [snippet] 내 해당 키워드를 강조 표시한다.
class ExploreResultCard extends StatelessWidget {
  /// [ExploreResultCard] 생성자.
  const ExploreResultCard({
    super.key,
    required this.title,
    this.subtitle,
    this.snippet,
    this.highlightKeyword,
    this.imageUrl,
    required this.onTap,
  });

  /// 약물명.
  final String title;

  /// 제조사명 등 부제목.
  final String? subtitle;

  /// 효능·부작용·주의사항 요약 텍스트.
  final String? snippet;

  /// 스니펫 내 강조할 키워드.
  final String? highlightKeyword;

  /// 약물 이미지 URL.
  final String? imageUrl;

  /// 카드 탭 콜백.
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
      ),
      elevation: 0,
      color: AppColors.surface,
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(12),
        child: Padding(
          padding: const EdgeInsets.all(12),
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              if (imageUrl != null && imageUrl!.isNotEmpty) ...[
                ClipRRect(
                  borderRadius: BorderRadius.circular(8),
                  child: Image.network(
                    imageUrl!,
                    width: 56,
                    height: 56,
                    fit: BoxFit.cover,
                    errorBuilder: (_, __, ___) => _buildPlaceholder(),
                  ),
                ),
                const SizedBox(width: 12),
              ],
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      title,
                      style: const TextStyle(
                        fontSize: 15,
                        fontWeight: FontWeight.w600,
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
                    if (snippet != null && snippet!.isNotEmpty) ...[
                      const SizedBox(height: 6),
                      _buildSnippet(),
                    ],
                  ],
                ),
              ),
              const SizedBox(width: 4),
              const Icon(
                Icons.chevron_right,
                color: AppColors.textDisabled,
                size: 20,
              ),
            ],
          ),
        ),
      ),
    );
  }

  /// 이미지 로드 실패 시 플레이스홀더를 생성한다.
  Widget _buildPlaceholder() {
    return Container(
      width: 56,
      height: 56,
      decoration: BoxDecoration(
        color: AppColors.primaryLight,
        borderRadius: BorderRadius.circular(8),
      ),
      child: const Icon(
        Icons.medication_outlined,
        color: AppColors.primary,
        size: 24,
      ),
    );
  }

  /// 스니펫 텍스트를 키워드 강조와 함께 구성한다.
  Widget _buildSnippet() {
    final text = _truncateSnippet(snippet!, 100);

    if (highlightKeyword == null || highlightKeyword!.isEmpty) {
      return Text(
        text,
        style: const TextStyle(
          fontSize: 12,
          color: AppColors.textSecondary,
          height: 1.4,
        ),
        maxLines: 2,
        overflow: TextOverflow.ellipsis,
      );
    }

    final spans = _buildHighlightedSpans(text, highlightKeyword!);
    return RichText(
      maxLines: 2,
      overflow: TextOverflow.ellipsis,
      text: TextSpan(
        style: const TextStyle(
          fontSize: 12,
          color: AppColors.textSecondary,
          height: 1.4,
        ),
        children: spans,
      ),
    );
  }

  /// 키워드를 강조 표시한 [TextSpan] 리스트를 생성한다.
  List<TextSpan> _buildHighlightedSpans(String text, String keyword) {
    final spans = <TextSpan>[];
    final lowerText = text.toLowerCase();
    final lowerKeyword = keyword.toLowerCase();
    var start = 0;

    while (start < text.length) {
      final index = lowerText.indexOf(lowerKeyword, start);
      if (index == -1) {
        spans.add(TextSpan(text: text.substring(start)));
        break;
      }
      if (index > start) {
        spans.add(TextSpan(text: text.substring(start, index)));
      }
      spans.add(
        TextSpan(
          text: text.substring(index, index + keyword.length),
          style: const TextStyle(
            color: AppColors.warning,
            fontWeight: FontWeight.w600,
            backgroundColor: Color(0x1AEA580C),
          ),
        ),
      );
      start = index + keyword.length;
    }

    return spans;
  }

  /// 스니펫을 최대 길이로 자른다.
  String _truncateSnippet(String text, int maxLength) {
    if (text.length <= maxLength) return text;
    return '${text.substring(0, maxLength)}...';
  }
}
