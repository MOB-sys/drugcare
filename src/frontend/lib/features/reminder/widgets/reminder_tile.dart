import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import 'package:yakmeogeo/core/theme/app_colors.dart';
import 'package:yakmeogeo/core/utils/date_utils.dart';
import 'package:yakmeogeo/features/reminder/models/reminder.dart';

/// 리마인더 리스트 아이템 타일.
///
/// 아이템 이름, 시간, 요일 칩, 메모를 표시하며
/// 활성/비활성 토글 스위치를 포함한다.
class ReminderTile extends StatelessWidget {
  /// [ReminderTile] 생성자.
  ///
  /// [reminder] — 표시할 리마인더.
  /// [onToggle] — 활성/비활성 토글 콜백.
  const ReminderTile({
    super.key,
    required this.reminder,
    required this.onToggle,
  });

  /// 표시할 리마인더.
  final Reminder reminder;

  /// 활성/비활성 토글 콜백.
  final VoidCallback onToggle;

  @override
  Widget build(BuildContext context) {
    final time = AppDateUtils.parseTime(reminder.reminderTime);
    final timeStr = AppDateUtils.formatTime(time.hour, time.minute);

    return Card(
      child: InkWell(
        borderRadius: BorderRadius.circular(12),
        onTap: () => context.push('/reminder/form', extra: reminder),
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
          child: Row(
            children: [
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    _buildItemHeader(timeStr),
                    _buildTimeAndMemo(),
                  ],
                ),
              ),
              SizedBox(
                width: 48,
                height: 48,
                child: FittedBox(
                  child: Switch(
                    value: reminder.isActive,
                    activeThumbColor: AppColors.primary,
                    onChanged: (_) => onToggle(),
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  /// 아이템 이름과 리마인더 시각을 표시하는 헤더 영역을 빌드한다.
  ///
  /// [timeStr] — 포맷된 시각 문자열 (예: "09:30").
  /// 활성 상태에 따라 텍스트 색상이 변경된다.
  Widget _buildItemHeader(String timeStr) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          reminder.itemName,
          style: TextStyle(
            fontSize: 16,
            fontWeight: FontWeight.w600,
            color: reminder.isActive
                ? AppColors.textPrimary
                : AppColors.textDisabled,
          ),
        ),
        const SizedBox(height: 4),
        Text(
          timeStr,
          style: TextStyle(
            fontSize: 24,
            fontWeight: FontWeight.bold,
            color: reminder.isActive
                ? AppColors.primary
                : AppColors.textDisabled,
          ),
        ),
      ],
    );
  }

  /// 요일 칩과 선택적 메모 텍스트를 표시하는 영역을 빌드한다.
  ///
  /// 요일 칩 행 아래에 메모가 존재하면 한 줄로 표시한다.
  Widget _buildTimeAndMemo() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const SizedBox(height: 6),
        _buildDayChips(),
        if (reminder.memo != null && reminder.memo!.isNotEmpty) ...[
          const SizedBox(height: 4),
          Text(
            reminder.memo!,
            style: const TextStyle(
              fontSize: 12,
              color: AppColors.textSecondary,
            ),
            maxLines: 1,
            overflow: TextOverflow.ellipsis,
          ),
        ],
      ],
    );
  }

  /// 요일 칩 행을 빌드한다.
  Widget _buildDayChips() {
    // daysOfWeek: 1=월~7=일, weekdayName index: 0=월~6=일
    final sorted = List<int>.from(reminder.daysOfWeek)..sort();

    return Wrap(
      spacing: 4,
      children: sorted.map((day) {
        final label = AppDateUtils.weekdayName(day - 1);
        return Container(
          padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
          decoration: BoxDecoration(
            color: reminder.isActive
                ? AppColors.primaryLight
                : AppColors.divider,
            borderRadius: BorderRadius.circular(4),
          ),
          child: Text(
            label,
            style: TextStyle(
              fontSize: 11,
              fontWeight: FontWeight.w500,
              color: reminder.isActive
                  ? AppColors.primaryDark
                  : AppColors.textDisabled,
            ),
          ),
        );
      }).toList(),
    );
  }
}
