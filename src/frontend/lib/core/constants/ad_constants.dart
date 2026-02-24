import 'dart:io';

/// 광고 관련 상수 (MVP: 테스트 ID만 사용).
class AdConstants {
  AdConstants._();

  /// AdMob 배너 광고 테스트 ID (Android).
  static const String androidBannerTestId =
      'ca-app-pub-3940256099942544/6300978111';

  /// AdMob 배너 광고 테스트 ID (iOS).
  static const String iosBannerTestId =
      'ca-app-pub-3940256099942544/2934735716';

  /// 플랫폼별 배너 광고 ID.
  static String get bannerAdUnitId {
    if (Platform.isAndroid) {
      return androidBannerTestId;
    } else if (Platform.isIOS) {
      return iosBannerTestId;
    }
    return androidBannerTestId;
  }
}
