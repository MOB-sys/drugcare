import 'package:flutter_local_notifications/flutter_local_notifications.dart';
import 'package:timezone/data/latest_all.dart' as tz;
import 'package:timezone/timezone.dart' as tz;

import 'package:yakmeogeo/features/reminder/models/reminder.dart';

/// 로컬 푸시 알림 서비스 — 싱글톤.
///
/// 리마인더 알림 스케줄링, 취소, 초기화를 담당한다.
class NotificationService {
  /// 싱글톤 강제용 private 생성자.
  NotificationService._();

  /// 싱글톤 인스턴스.
  static final NotificationService instance = NotificationService._();

  /// Flutter 로컬 알림 플러그인 인스턴스.
  final FlutterLocalNotificationsPlugin _plugin =
      FlutterLocalNotificationsPlugin();

  /// 초기화 완료 여부.
  bool _initialized = false;

  /// 알림 플러그인을 초기화한다.
  ///
  /// Android 채널 생성, iOS 권한 요청, timezone 설정을 수행한다.
  /// 앱 시작 시 한 번만 호출한다.
  Future<void> initialize() async {
    if (_initialized) return;

    // Timezone 초기화
    tz.initializeTimeZones();
    tz.setLocalLocation(tz.getLocation('Asia/Seoul'));

    // Android 설정
    const androidSettings =
        AndroidInitializationSettings('@mipmap/ic_launcher');

    // iOS 설정
    const iosSettings = DarwinInitializationSettings(
      requestAlertPermission: true,
      requestBadgePermission: true,
      requestSoundPermission: true,
    );

    const settings = InitializationSettings(
      android: androidSettings,
      iOS: iosSettings,
    );

    await _plugin.initialize(settings);

    // Android 알림 채널 생성
    await _plugin
        .resolvePlatformSpecificImplementation<
            AndroidFlutterLocalNotificationsPlugin>()
        ?.createNotificationChannel(
          const AndroidNotificationChannel(
            'yakmeogeo_reminder',
            '복약 리마인더',
            description: '약 먹을 시간 알림',
            importance: Importance.high,
          ),
        );

    _initialized = true;
  }

  /// 리마인더에 대한 주간 반복 알림을 스케줄링한다.
  ///
  /// [reminder]의 각 요일에 대해 개별 알림을 등록한다.
  /// 알림 ID: `reminder.id * 10 + dayIndex` (요일별 고유 ID).
  Future<void> scheduleReminder(Reminder reminder) async {
    if (!reminder.isActive) return;

    // reminderTime 파싱 (HH:mm:ss)
    final timeParts = reminder.reminderTime.split(':');
    final hour = int.parse(timeParts[0]);
    final minute = int.parse(timeParts[1]);

    const androidDetails = AndroidNotificationDetails(
      'yakmeogeo_reminder',
      '복약 리마인더',
      channelDescription: '약 먹을 시간 알림',
      importance: Importance.high,
      priority: Priority.high,
    );

    const iosDetails = DarwinNotificationDetails(
      presentAlert: true,
      presentBadge: true,
      presentSound: true,
    );

    const details = NotificationDetails(
      android: androidDetails,
      iOS: iosDetails,
    );

    final body = reminder.memo != null && reminder.memo!.isNotEmpty
        ? '${reminder.itemName} ${reminder.memo}'
        : reminder.itemName;

    for (var i = 0; i < reminder.daysOfWeek.length; i++) {
      final dayOfWeek = reminder.daysOfWeek[i];
      final notificationId = reminder.id * 10 + dayOfWeek;

      // flutter_local_notifications의 Day: 1=Monday ~ 7=Sunday
      // Reminder의 daysOfWeek: 1=월 ~ 7=일 (동일 매핑)
      await _plugin.zonedSchedule(
        notificationId,
        '약 먹을 시간이에요!',
        body,
        _nextInstanceOfWeekday(dayOfWeek, hour, minute),
        details,
        androidScheduleMode: AndroidScheduleMode.inexactAllowWhileIdle,
        uiLocalNotificationDateInterpretation:
            UILocalNotificationDateInterpretation.absoluteTime,
        matchDateTimeComponents: DateTimeComponents.dayOfWeekAndTime,
      );
    }
  }

  /// 리마인더의 모든 알림을 취소한다.
  ///
  /// [reminderId]에 해당하는 요일별 알림 슬롯(id*10+1 ~ id*10+7)을 취소한다.
  Future<void> cancelReminder(int reminderId) async {
    for (var day = 1; day <= 7; day++) {
      await _plugin.cancel(reminderId * 10 + day);
    }
  }

  /// 모든 알림을 취소한다.
  Future<void> cancelAll() async {
    await _plugin.cancelAll();
  }

  /// 다음 [weekday] [hour]:[minute]의 TZDateTime을 계산한다.
  tz.TZDateTime _nextInstanceOfWeekday(int weekday, int hour, int minute) {
    final now = tz.TZDateTime.now(tz.local);
    var scheduled = tz.TZDateTime(
      tz.local,
      now.year,
      now.month,
      now.day,
      hour,
      minute,
    );

    // weekday 맞추기: DateTime의 weekday (1=Monday ~ 7=Sunday)
    while (scheduled.weekday != weekday) {
      scheduled = scheduled.add(const Duration(days: 1));
    }

    // 이미 지난 시간이면 다음 주로
    if (scheduled.isBefore(now)) {
      scheduled = scheduled.add(const Duration(days: 7));
    }

    return scheduled;
  }
}
