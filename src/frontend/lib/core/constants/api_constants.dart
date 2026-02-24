/// API 관련 상수 정의.
class ApiConstants {
  ApiConstants._();

  /// 백엔드 기본 URL (개발 환경).
  static const String baseUrl = 'http://localhost:8000';

  /// API 버전 접두사.
  static const String apiPrefix = '/api/v1';

  // ── 약물 (Drugs) ──
  /// 약물 검색.
  static const String drugSearch = '$apiPrefix/drugs/search';

  /// 약물 상세 (drug_id 치환 필요).
  static String drugDetail(int drugId) => '$apiPrefix/drugs/$drugId';

  // ── 영양제 (Supplements) ──
  /// 영양제 검색.
  static const String supplementSearch = '$apiPrefix/supplements/search';

  /// 영양제 상세 (supplement_id 치환 필요).
  static String supplementDetail(int supplementId) =>
      '$apiPrefix/supplements/$supplementId';

  // ── 상호작용 (Interactions) ──
  /// 상호작용 체크.
  static const String interactionCheck = '$apiPrefix/interactions/check';

  // ── 복약함 (Cabinet) ──
  /// 복약함 아이템 목록 / 추가.
  static const String cabinet = '$apiPrefix/cabinet';

  /// 복약함 아이템 삭제 (item_id 치환 필요).
  static String cabinetItem(int itemId) => '$apiPrefix/cabinet/$itemId';

  // ── 리마인더 (Reminders) ──
  /// 리마인더 목록 / 생성.
  static const String reminders = '$apiPrefix/reminders';

  /// 리마인더 수정 / 삭제 (reminder_id 치환 필요).
  static String reminder(int reminderId) =>
      '$apiPrefix/reminders/$reminderId';

  // ── 피드백 (Feedback) ──
  /// 피드백 제출.
  static const String feedback = '$apiPrefix/feedback';

  // ── 메트릭스 (Metrics) ──
  /// 앱 메트릭스 이벤트 기록.
  static const String metrics = '$apiPrefix/metrics/event';

  // ── 헬스체크 ──
  /// 서버 헬스체크.
  static const String health = '$apiPrefix/health';

  // ── 헤더 ──
  /// 디바이스 ID 헤더명.
  static const String deviceIdHeader = 'X-Device-ID';
}
