import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import 'package:pillright/core/theme/app_colors.dart';
import 'package:pillright/features/reminder/providers/reminder_provider.dart';
import 'package:pillright/features/reminder/widgets/reminder_tile.dart';
import 'package:pillright/shared/widgets/common/empty_state_widget.dart';
import 'package:pillright/shared/widgets/common/error_widget.dart';
import 'package:pillright/shared/widgets/common/loading_widget.dart';

/// 리마인더 목록 화면.
///
/// 등록된 복약 리마인더를 리스트로 표시한다.
/// 활성만/전체 보기 필터, 추가(FAB), 스와이프 삭제를 지원한다.
class ReminderScreen extends ConsumerWidget {
  /// [ReminderScreen] 생성자.
  const ReminderScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final reminderState = ref.watch(reminderProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('복약 리마인더'),
        actions: [
          TextButton.icon(
            onPressed: () =>
                ref.read(reminderProvider.notifier).toggleShowAll(),
            icon: Icon(
              reminderState.showAll
                  ? Icons.filter_alt
                  : Icons.filter_alt_off,
              size: 20,
            ),
            label: Text(
              reminderState.showAll ? '활성만' : '전체',
              style: const TextStyle(fontSize: 13),
            ),
          ),
        ],
      ),
      body: reminderState.reminders.when(
        loading: () => const LoadingWidget(message: '리마인더를 불러오는 중...'),
        error: (err, _) => AppErrorWidget(
          message: err.toString(),
          onRetry: () =>
              ref.read(reminderProvider.notifier).loadReminders(),
        ),
        data: (reminders) {
          if (reminders.isEmpty) {
            return const EmptyStateWidget(
              message: '등록된 리마인더가 없습니다.\n+ 버튼을 눌러 추가해 보세요.',
              icon: Icons.alarm_off,
            );
          }

          return ListView.builder(
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
            itemCount: reminders.length,
            itemBuilder: (context, index) {
              final reminder = reminders[index];

              return Dismissible(
                key: ValueKey(reminder.id),
                direction: DismissDirection.endToStart,
                background: Container(
                  alignment: Alignment.centerRight,
                  padding: const EdgeInsets.only(right: 20),
                  margin: const EdgeInsets.symmetric(vertical: 4),
                  decoration: BoxDecoration(
                    color: AppColors.danger,
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: const Icon(
                    Icons.delete,
                    color: Colors.white,
                  ),
                ),
                confirmDismiss: (_) => _confirmDelete(context),
                onDismissed: (_) {
                  ref
                      .read(reminderProvider.notifier)
                      .deleteReminder(reminder.id);
                },
                child: ReminderTile(
                  reminder: reminder,
                  onToggle: () => ref
                      .read(reminderProvider.notifier)
                      .toggleActive(reminder),
                ),
              );
            },
          );
        },
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: () => context.push('/reminder/form'),
        backgroundColor: AppColors.primary,
        child: const Icon(Icons.add, color: Colors.white),
      ),
    );
  }

  /// 삭제 확인 다이얼로그를 표시한다.
  Future<bool> _confirmDelete(BuildContext context) async {
    final result = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('리마인더 삭제'),
        content: const Text('이 리마인더를 삭제하시겠습니까?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(ctx).pop(false),
            child: const Text('취소'),
          ),
          TextButton(
            onPressed: () => Navigator.of(ctx).pop(true),
            style: TextButton.styleFrom(foregroundColor: AppColors.danger),
            child: const Text('삭제'),
          ),
        ],
      ),
    );
    return result ?? false;
  }
}
