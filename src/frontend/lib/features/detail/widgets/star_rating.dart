import 'package:flutter/material.dart';

/// 별점 표시/입력 위젯.
///
/// [interactive]가 true이면 탭으로 별점을 변경할 수 있다.
class StarRating extends StatelessWidget {
  /// 현재 별점 (1~5).
  final int rating;

  /// 별점 변경 콜백 (interactive 모드에서만 호출).
  final ValueChanged<int>? onChanged;

  /// 인터랙티브 모드 여부.
  final bool interactive;

  /// 별 아이콘 크기.
  final double size;

  /// 별 색상.
  final Color? color;

  /// [StarRating] 생성자.
  const StarRating({
    super.key,
    required this.rating,
    this.onChanged,
    this.interactive = false,
    this.size = 20,
    this.color,
  });

  @override
  Widget build(BuildContext context) {
    final starColor = color ?? Colors.amber;

    return Row(
      mainAxisSize: MainAxisSize.min,
      children: List.generate(5, (index) {
        final starIndex = index + 1;
        final icon = starIndex <= rating
            ? Icons.star
            : Icons.star_border;

        if (interactive) {
          return GestureDetector(
            onTap: () => onChanged?.call(starIndex),
            child: Padding(
              padding: const EdgeInsets.symmetric(horizontal: 2),
              child: Icon(icon, size: size, color: starColor),
            ),
          );
        }

        return Padding(
          padding: const EdgeInsets.symmetric(horizontal: 1),
          child: Icon(icon, size: size, color: starColor),
        );
      }),
    );
  }
}
