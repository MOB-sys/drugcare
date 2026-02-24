import 'package:intl/intl.dart';

/// 날짜/시간 포맷 유틸.
class AppDateUtils {
  AppDateUtils._();

  /// 한국어 요일 이름 (0=월, 1=화, ..., 6=일).
  static const List<String> weekdayNames = [
    '월', '화', '수', '목', '금', '토', '일',
  ];

  /// 요일 인덱스(0~6)를 한국어 요일로 변환한다.
  static String weekdayName(int index) {
    if (index < 0 || index > 6) return '';
    return weekdayNames[index];
  }

  /// 요일 인덱스 리스트를 '월,수,금' 형태 문자열로 변환한다.
  static String formatDaysOfWeek(List<int> days) {
    final sorted = List<int>.from(days)..sort();
    return sorted.map(weekdayName).join(', ');
  }

  /// TimeOfDay 형태의 시간을 'HH:mm' 문자열로 변환한다.
  static String formatTime(int hour, int minute) {
    return '${hour.toString().padLeft(2, '0')}:${minute.toString().padLeft(2, '0')}';
  }

  /// 'HH:mm:ss' 또는 'HH:mm' 문자열을 시/분 파싱한다.
  static ({int hour, int minute}) parseTime(String timeStr) {
    final parts = timeStr.split(':');
    return (
      hour: int.parse(parts[0]),
      minute: int.parse(parts[1]),
    );
  }

  /// DateTime을 'yyyy-MM-dd' 형태로 포맷한다.
  static String formatDate(DateTime date) {
    return DateFormat('yyyy-MM-dd').format(date);
  }

  /// DateTime을 'yyyy-MM-dd HH:mm' 형태로 포맷한다.
  static String formatDateTime(DateTime date) {
    return DateFormat('yyyy-MM-dd HH:mm').format(date);
  }
}
