/// 앱 전역 상수 정의.
class AppConstants {
  AppConstants._();

  /// 앱 이름.
  static const String appName = '약먹어';

  /// 앱 부제.
  static const String appTagline = '이 약이랑 이 영양제, 같이 먹어도 돼?';

  /// 면책조항 텍스트.
  static const String disclaimer =
      '이 정보는 참고용이며, 의사/약사의 전문적 판단을 대체하지 않습니다.';

  /// 면책조항 상세.
  static const String disclaimerDetail =
      '약먹어에서 제공하는 정보는 공공 데이터를 기반으로 한 참고 정보입니다. '
      '실제 복약 관련 결정은 반드시 담당 의사 또는 약사와 상의하세요.';

  /// 검색 결과 기본 페이지 사이즈.
  static const int defaultPageSize = 20;

  /// 최대 상호작용 체크 아이템 수.
  static const int maxInteractionItems = 20;

  /// 최소 상호작용 체크 아이템 수.
  static const int minInteractionItems = 2;

  /// 검색 디바운스 (밀리초).
  static const int searchDebounceMs = 500;

  /// SharedPreferences 키: 디바이스 ID.
  static const String deviceIdKey = 'device_id';

  /// 건강팁 정적 리스트.
  static const List<String> healthTips = [
    '약은 반드시 물과 함께 복용하세요.',
    '자몽주스는 일부 약물의 효과에 영향을 줄 수 있습니다.',
    '철분제는 공복에, 칼슘제는 식후에 복용하면 흡수율이 높아집니다.',
    '항생제 복용 시 유제품 섭취를 피하세요.',
    '비타민C와 철분제를 함께 복용하면 철분 흡수가 도움됩니다.',
    '혈압약은 매일 같은 시간에 복용하는 것이 중요합니다.',
    '오메가3는 식사와 함께 복용해야 흡수율이 높아집니다.',
    '카페인은 일부 진통제의 효과를 높이지만, 수면제와는 함께 복용하지 마세요.',
  ];
}
