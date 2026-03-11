import 'package:flutter/material.dart';

/// 상세 화면 정보 섹션.
///
/// 아이콘 + 제목 헤더와 자식 위젯을 카드 안에 표시한다.
class InfoSection extends StatelessWidget {
  /// 섹션 제목.
  final String title;

  /// 섹션 아이콘.
  final IconData icon;

  /// 섹션 내용 위젯.
  final Widget child;

  /// [InfoSection] 생성자.
  const InfoSection({
    super.key,
    required this.title,
    required this.icon,
    required this.child,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(icon, size: 20, color: theme.colorScheme.primary),
                const SizedBox(width: 8),
                Text(
                  title,
                  style: theme.textTheme.titleSmall?.copyWith(
                    fontWeight: FontWeight.w700,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            child,
          ],
        ),
      ),
    );
  }
}
