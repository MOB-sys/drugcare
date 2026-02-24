/// 리마인더 (서버 응답).
class Reminder {
  /// 리마인더 ID.
  final int id;

  /// 디바이스 ID.
  final String deviceId;

  /// 복약함 아이템 ID.
  final int cabinetItemId;

  /// 아이템 이름.
  final String itemName;

  /// 알림 시간 (HH:mm:ss 형식).
  final String reminderTime;

  /// 요일 목록 (1=월 ~ 7=일).
  final List<int> daysOfWeek;

  /// 활성 여부.
  final bool isActive;

  /// 메모.
  final String? memo;

  /// 생성 일시.
  final DateTime createdAt;

  /// [Reminder] 생성자.
  const Reminder({
    required this.id,
    required this.deviceId,
    required this.cabinetItemId,
    required this.itemName,
    required this.reminderTime,
    required this.daysOfWeek,
    required this.isActive,
    this.memo,
    required this.createdAt,
  });

  /// JSON에서 [Reminder]를 생성한다.
  factory Reminder.fromJson(Map<String, dynamic> json) {
    return Reminder(
      id: json['id'] as int,
      deviceId: json['device_id'] as String,
      cabinetItemId: json['cabinet_item_id'] as int,
      itemName: json['item_name'] as String,
      reminderTime: json['reminder_time'] as String,
      daysOfWeek: (json['days_of_week'] as List).cast<int>(),
      isActive: json['is_active'] as bool,
      memo: json['memo'] as String?,
      createdAt: DateTime.parse(json['created_at'] as String),
    );
  }
}

/// 리마인더 생성 요청.
class ReminderCreate {
  /// 복약함 아이템 ID.
  final int cabinetItemId;

  /// 알림 시간 (HH:mm:ss 형식).
  final String reminderTime;

  /// 요일 목록 (1=월 ~ 7=일).
  final List<int> daysOfWeek;

  /// 메모.
  final String? memo;

  /// [ReminderCreate] 생성자.
  const ReminderCreate({
    required this.cabinetItemId,
    required this.reminderTime,
    required this.daysOfWeek,
    this.memo,
  });

  /// JSON으로 변환한다.
  Map<String, dynamic> toJson() {
    return {
      'cabinet_item_id': cabinetItemId,
      'reminder_time': reminderTime,
      'days_of_week': daysOfWeek,
      'memo': memo,
    };
  }
}

/// 리마인더 수정 요청.
class ReminderUpdate {
  /// 알림 시간 (HH:mm:ss 형식).
  final String? reminderTime;

  /// 요일 목록 (1=월 ~ 7=일).
  final List<int>? daysOfWeek;

  /// 활성 여부.
  final bool? isActive;

  /// 메모.
  final String? memo;

  /// [ReminderUpdate] 생성자.
  const ReminderUpdate({
    this.reminderTime,
    this.daysOfWeek,
    this.isActive,
    this.memo,
  });

  /// JSON으로 변환한다 (null이 아닌 필드만 포함).
  Map<String, dynamic> toJson() {
    final json = <String, dynamic>{};
    if (reminderTime != null) json['reminder_time'] = reminderTime;
    if (daysOfWeek != null) json['days_of_week'] = daysOfWeek;
    if (isActive != null) json['is_active'] = isActive;
    if (memo != null) json['memo'] = memo;
    return json;
  }
}
