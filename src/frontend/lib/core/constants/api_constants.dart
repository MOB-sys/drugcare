/// API 관련 상수 정의.
class ApiConstants {
  ApiConstants._();

  /// 백엔드 기본 URL (빌드 시 --dart-define=API_BASE_URL 로 오버라이드).
  ///
  /// 릴리스 빌드에서는 반드시 HTTPS URL을 지정해야 한다.
  static const String baseUrl = String.fromEnvironment(
    'API_BASE_URL',
    defaultValue: 'http://localhost:8000',
  );

  /// API 버전 접두사.
  static const String apiPrefix = '/api/v1';

  // ── 약물 (Drugs) ──
  /// 약물 검색.
  static const String drugSearch = '$apiPrefix/drugs/search';

  /// 약물 상세 (drug_id 치환 필요).
  static String drugDetail(int drugId) => '$apiPrefix/drugs/$drugId';

  /// 증상별 약물 검색.
  static const String drugSymptomSearch = '$apiPrefix/drugs/symptoms/search';

  /// 부작용 역검색.
  static const String drugSideEffectSearch =
      '$apiPrefix/drugs/side-effects/search';

  /// 질환별 주의약물 검색.
  static const String drugConditionSearch =
      '$apiPrefix/drugs/conditions/search';

  /// 알약 식별.
  static const String drugIdentify = '$apiPrefix/drugs/identify';

  /// 최근 등록 약물.
  static const String drugRecent = '$apiPrefix/drugs/recent';

  // ── 영양제 (Supplements) ──
  /// 영양제 검색.
  static const String supplementSearch = '$apiPrefix/supplements/search';

  /// 영양제 상세 (supplement_id 치환 필요).
  static String supplementDetail(int supplementId) =>
      '$apiPrefix/supplements/$supplementId';

  // ── 식품 (Foods) ──
  /// 식품 검색.
  static const String foodSearch = '$apiPrefix/foods/search';

  /// 식품 상세 (food_id 치환 필요).
  static String foodDetail(int foodId) => '$apiPrefix/foods/$foodId';

  /// 식품 슬러그 조회.
  static String foodBySlug(String slug) => '$apiPrefix/foods/by-slug/$slug';

  // ── 한약재 (Herbal Medicines) ──
  /// 한약재 검색.
  static const String herbalMedicineSearch =
      '$apiPrefix/herbal-medicines/search';

  /// 한약재 상세 (herbal_medicine_id 치환 필요).
  static String herbalMedicineDetail(int herbalMedicineId) =>
      '$apiPrefix/herbal-medicines/$herbalMedicineId';

  /// 한약재 슬러그 조회.
  static String herbalMedicineBySlug(String slug) =>
      '$apiPrefix/herbal-medicines/by-slug/$slug';

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

  // ── 리뷰 (Reviews) ──
  /// 리뷰 작성.
  static const String reviews = '$apiPrefix/reviews';

  /// 리뷰 목록 조회.
  static String reviewList(String itemType, int itemId) =>
      '$apiPrefix/reviews/$itemType/$itemId';

  /// 리뷰 통계 조회.
  static String reviewSummary(String itemType, int itemId) =>
      '$apiPrefix/reviews/$itemType/$itemId/summary';

  /// 리뷰 도움됨.
  static String reviewHelpful(int reviewId) =>
      '$apiPrefix/reviews/$reviewId/helpful';

  /// 리뷰 삭제.
  static String reviewDelete(int reviewId) =>
      '$apiPrefix/reviews/$reviewId';

  // ── 헬스체크 ──
  /// 서버 헬스체크.
  static const String health = '$apiPrefix/health';

  // ── 헤더 ──
  /// 디바이스 ID 헤더명.
  static const String deviceIdHeader = 'X-Device-ID';
}
