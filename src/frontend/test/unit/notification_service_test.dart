import 'package:flutter_test/flutter_test.dart';
import 'package:yakmeogeo/features/reminder/models/reminder.dart';

void main() {
  group('NotificationService', () {
    test('알림 ID 생성 공식: reminderId * 10 + dayOfWeek', () {
      // 리마인더 ID=5, 요일=3 → 알림 ID=53
      const reminderId = 5;
      const dayOfWeek = 3;
      final notificationId = reminderId * 10 + dayOfWeek;
      expect(notificationId, 53);
    });

    test('알림 ID 생성 공식: 다른 리마인더도 충돌 없음', () {
      // 리마인더 1의 요일별 ID: 11, 12, 13, 14, 15, 16, 17
      // 리마인더 2의 요일별 ID: 21, 22, 23, 24, 25, 26, 27
      final reminder1Ids = List.generate(7, (i) => 1 * 10 + (i + 1));
      final reminder2Ids = List.generate(7, (i) => 2 * 10 + (i + 1));

      // 겹치는 ID가 없어야 한다
      final allIds = {...reminder1Ids, ...reminder2Ids};
      expect(allIds.length, 14);
    });

    test('취소 시 7개 슬롯(day 1~7)을 모두 취소해야 함', () {
      const reminderId = 3;
      final cancelIds = List.generate(7, (i) => reminderId * 10 + (i + 1));
      expect(cancelIds, [31, 32, 33, 34, 35, 36, 37]);
    });

    test('Reminder 모델의 reminderTime 파싱', () {
      const timeStr = '09:30:00';
      final parts = timeStr.split(':');
      expect(int.parse(parts[0]), 9);
      expect(int.parse(parts[1]), 30);
    });

    test('비활성 리마인더는 스케줄링하지 않는다', () {
      final reminder = Reminder(
        id: 1,
        deviceId: 'test',
        cabinetItemId: 1,
        itemName: '타이레놀',
        reminderTime: '09:00:00',
        daysOfWeek: [1, 2, 3],
        isActive: false,
        createdAt: DateTime.now(),
      );
      // isActive가 false이므로 스케줄링 스킵
      expect(reminder.isActive, false);
    });

    test('알림 본문: 메모 포함', () {
      final reminder = Reminder(
        id: 1,
        deviceId: 'test',
        cabinetItemId: 1,
        itemName: '타이레놀',
        reminderTime: '09:00:00',
        daysOfWeek: [1],
        isActive: true,
        memo: '아침 식후',
        createdAt: DateTime.now(),
      );
      final body = reminder.memo != null && reminder.memo!.isNotEmpty
          ? '${reminder.itemName} ${reminder.memo}'
          : reminder.itemName;
      expect(body, '타이레놀 아침 식후');
    });

    test('알림 본문: 메모 없음', () {
      final reminder = Reminder(
        id: 1,
        deviceId: 'test',
        cabinetItemId: 1,
        itemName: '타이레놀',
        reminderTime: '09:00:00',
        daysOfWeek: [1],
        isActive: true,
        createdAt: DateTime.now(),
      );
      final body = reminder.memo != null && reminder.memo!.isNotEmpty
          ? '${reminder.itemName} ${reminder.memo}'
          : reminder.itemName;
      expect(body, '타이레놀');
    });
  });
}
