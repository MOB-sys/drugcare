import 'package:flutter_test/flutter_test.dart';
import 'package:yakmeogeo/core/utils/date_utils.dart';

void main() {
  group('AppDateUtils', () {
    group('weekdayName', () {
      test('0~6 인덱스를 한국어 요일로 변환한다', () {
        expect(AppDateUtils.weekdayName(0), '월');
        expect(AppDateUtils.weekdayName(1), '화');
        expect(AppDateUtils.weekdayName(2), '수');
        expect(AppDateUtils.weekdayName(3), '목');
        expect(AppDateUtils.weekdayName(4), '금');
        expect(AppDateUtils.weekdayName(5), '토');
        expect(AppDateUtils.weekdayName(6), '일');
      });

      test('범위 밖 인덱스는 빈 문자열을 반환한다', () {
        expect(AppDateUtils.weekdayName(-1), '');
        expect(AppDateUtils.weekdayName(7), '');
        expect(AppDateUtils.weekdayName(100), '');
      });
    });

    group('formatDaysOfWeek', () {
      test('요일 인덱스 리스트를 한국어 요일 문자열로 변환한다', () {
        expect(AppDateUtils.formatDaysOfWeek([0, 2, 4]), '월, 수, 금');
      });

      test('정렬되지 않은 리스트도 정렬하여 변환한다', () {
        expect(AppDateUtils.formatDaysOfWeek([4, 0, 2]), '월, 수, 금');
      });

      test('빈 리스트는 빈 문자열을 반환한다', () {
        expect(AppDateUtils.formatDaysOfWeek([]), '');
      });

      test('단일 요일도 변환한다', () {
        expect(AppDateUtils.formatDaysOfWeek([3]), '목');
      });

      test('모든 요일을 변환한다', () {
        expect(
          AppDateUtils.formatDaysOfWeek([0, 1, 2, 3, 4, 5, 6]),
          '월, 화, 수, 목, 금, 토, 일',
        );
      });
    });

    group('formatTime', () {
      test('한 자리 시간과 분을 0으로 패딩한다', () {
        expect(AppDateUtils.formatTime(9, 0), '09:00');
      });

      test('두 자리 시간과 분을 올바르게 포맷한다', () {
        expect(AppDateUtils.formatTime(23, 59), '23:59');
      });

      test('자정을 올바르게 포맷한다', () {
        expect(AppDateUtils.formatTime(0, 0), '00:00');
      });

      test('정오를 올바르게 포맷한다', () {
        expect(AppDateUtils.formatTime(12, 30), '12:30');
      });
    });

    group('parseTime', () {
      test('HH:mm 문자열을 시/분으로 파싱한다', () {
        final result = AppDateUtils.parseTime('09:00');
        expect(result.hour, 9);
        expect(result.minute, 0);
      });

      test('HH:mm:ss 문자열도 시/분으로 파싱한다', () {
        final result = AppDateUtils.parseTime('23:59:00');
        expect(result.hour, 23);
        expect(result.minute, 59);
      });

      test('자정을 파싱한다', () {
        final result = AppDateUtils.parseTime('00:00');
        expect(result.hour, 0);
        expect(result.minute, 0);
      });
    });

    group('formatDate', () {
      test('DateTime을 yyyy-MM-dd 형태로 포맷한다', () {
        final date = DateTime(2026, 2, 24);
        expect(AppDateUtils.formatDate(date), '2026-02-24');
      });

      test('한 자리 월/일을 0으로 패딩한다', () {
        final date = DateTime(2026, 1, 5);
        expect(AppDateUtils.formatDate(date), '2026-01-05');
      });
    });

    group('formatDateTime', () {
      test('DateTime을 yyyy-MM-dd HH:mm 형태로 포맷한다', () {
        final date = DateTime(2026, 2, 24, 14, 30);
        expect(AppDateUtils.formatDateTime(date), '2026-02-24 14:30');
      });

      test('자정 시간을 올바르게 포맷한다', () {
        final date = DateTime(2026, 1, 1, 0, 0);
        expect(AppDateUtils.formatDateTime(date), '2026-01-01 00:00');
      });
    });
  });
}
