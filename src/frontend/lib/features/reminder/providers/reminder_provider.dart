import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'package:yakmeogeo/core/providers/service_providers.dart';
import 'package:yakmeogeo/features/reminder/models/reminder.dart';

/// 리마인더 화면 상태.
class ReminderState {
  /// 리마인더 목록 (비동기).
  final AsyncValue<List<Reminder>> reminders;

  /// 전체 보기 여부 (false면 활성만).
  final bool showAll;

  /// [ReminderState] 생성자.
  const ReminderState({
    this.reminders = const AsyncValue.loading(),
    this.showAll = false,
  });

  /// 상태를 복사하며 일부 필드를 변경한다.
  ReminderState copyWith({
    AsyncValue<List<Reminder>>? reminders,
    bool? showAll,
  }) {
    return ReminderState(
      reminders: reminders ?? this.reminders,
      showAll: showAll ?? this.showAll,
    );
  }
}

/// 리마인더 상태 관리 노티파이어.
class ReminderNotifier extends StateNotifier<ReminderState> {
  /// 리마인더 서비스 참조.
  final Ref _ref;

  /// [ReminderNotifier] 생성자.
  ReminderNotifier(this._ref) : super(const ReminderState()) {
    loadReminders();
  }

  /// 리마인더 목록을 서버에서 불러온다.
  Future<void> loadReminders() async {
    state = state.copyWith(reminders: const AsyncValue.loading());
    try {
      final service = _ref.read(reminderServiceProvider);
      final list = await service.listReminders(activeOnly: !state.showAll);
      state = state.copyWith(reminders: AsyncValue.data(list));
    } catch (e, st) {
      state = state.copyWith(reminders: AsyncValue.error(e, st));
    }
  }

  /// 새 리마인더를 생성하고 목록을 갱신한다.
  Future<void> createReminder(ReminderCreate create) async {
    final service = _ref.read(reminderServiceProvider);
    await service.createReminder(create);
    await loadReminders();
  }

  /// 리마인더를 수정하고 목록을 갱신한다.
  Future<void> updateReminder(int id, ReminderUpdate update) async {
    final service = _ref.read(reminderServiceProvider);
    await service.updateReminder(id, update);
    await loadReminders();
  }

  /// 리마인더 활성/비활성 상태를 토글한다.
  Future<void> toggleActive(Reminder reminder) async {
    await updateReminder(
      reminder.id,
      ReminderUpdate(isActive: !reminder.isActive),
    );
  }

  /// 리마인더를 삭제하고 목록을 갱신한다.
  Future<void> deleteReminder(int id) async {
    final service = _ref.read(reminderServiceProvider);
    await service.deleteReminder(id);
    await loadReminders();
  }

  /// 전체 보기/활성만 보기를 토글한다.
  Future<void> toggleShowAll() async {
    state = state.copyWith(showAll: !state.showAll);
    await loadReminders();
  }
}

/// 리마인더 상태 프로바이더.
final reminderProvider =
    StateNotifierProvider<ReminderNotifier, ReminderState>((ref) {
  return ReminderNotifier(ref);
});
