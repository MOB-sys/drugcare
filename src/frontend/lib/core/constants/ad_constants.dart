import 'dart:io';

/// 광고 관련 상수 (MVP: 테스트 ID만 사용).
class AdConstants {
  AdConstants._();

  // ---------------------------------------------------------------------------
  // 배너 광고
  // ---------------------------------------------------------------------------

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

  // ---------------------------------------------------------------------------
  // 전면 광고 (Interstitial)
  // ---------------------------------------------------------------------------

  /// AdMob 전면 광고 테스트 ID (Android).
  static const String androidInterstitialTestId =
      'ca-app-pub-3940256099942544/1033173712';

  /// AdMob 전면 광고 테스트 ID (iOS).
  static const String iosInterstitialTestId =
      'ca-app-pub-3940256099942544/4411468910';

  /// 플랫폼별 전면 광고 ID.
  static String get interstitialAdUnitId {
    if (Platform.isAndroid) {
      return androidInterstitialTestId;
    } else if (Platform.isIOS) {
      return iosInterstitialTestId;
    }
    return androidInterstitialTestId;
  }

  // ---------------------------------------------------------------------------
  // 네이티브 광고 (Native)
  // ---------------------------------------------------------------------------

  /// AdMob 네이티브 광고 테스트 ID (Android).
  static const String androidNativeTestId =
      'ca-app-pub-3940256099942544/2247696110';

  /// AdMob 네이티브 광고 테스트 ID (iOS).
  static const String iosNativeTestId =
      'ca-app-pub-3940256099942544/3986624511';

  /// 플랫폼별 네이티브 광고 ID.
  static String get nativeAdUnitId {
    if (Platform.isAndroid) {
      return androidNativeTestId;
    } else if (Platform.isIOS) {
      return iosNativeTestId;
    }
    return androidNativeTestId;
  }

  // ---------------------------------------------------------------------------
  // 광고 빈도 제한
  // ---------------------------------------------------------------------------

  /// 전면 광고 최소 노출 간격 (밀리초).
  static const int interstitialMinIntervalMs = 3 * 60 * 1000; // 3분
}
