import 'dart:io';

/// 광고 관련 상수.
/// 프로덕션 빌드 시 `--dart-define` 으로 실제 ID를 주입한다.
/// 예: `flutter build appbundle --dart-define=ADMOB_ANDROID_BANNER=ca-app-pub-xxx`
/// 기본값은 Google 공식 테스트 ID (개발/테스트 호환).
class AdConstants {
  /// 인스턴스 생성 방지용 private 생성자.
  AdConstants._();

  // ---------------------------------------------------------------------------
  // 배너 광고
  // ---------------------------------------------------------------------------

  /// AdMob 배너 광고 ID (Android).
  static const String androidBannerId = String.fromEnvironment(
    'ADMOB_ANDROID_BANNER',
    defaultValue: 'ca-app-pub-4091950246368818/8420353670',
  );

  /// AdMob 배너 광고 ID (iOS).
  static const String iosBannerId = String.fromEnvironment(
    'ADMOB_IOS_BANNER',
    defaultValue: 'ca-app-pub-3940256099942544/2934735716',
  );

  /// 플랫폼별 배너 광고 ID.
  static String get bannerAdUnitId {
    if (Platform.isAndroid) return androidBannerId;
    if (Platform.isIOS) return iosBannerId;
    return androidBannerId;
  }

  // ---------------------------------------------------------------------------
  // 전면 광고 (Interstitial)
  // ---------------------------------------------------------------------------

  /// AdMob 전면 광고 ID (Android).
  static const String androidInterstitialId = String.fromEnvironment(
    'ADMOB_ANDROID_INTERSTITIAL',
    defaultValue: 'ca-app-pub-3940256099942544/1033173712',
  );

  /// AdMob 전면 광고 ID (iOS).
  static const String iosInterstitialId = String.fromEnvironment(
    'ADMOB_IOS_INTERSTITIAL',
    defaultValue: 'ca-app-pub-3940256099942544/4411468910',
  );

  /// 플랫폼별 전면 광고 ID.
  static String get interstitialAdUnitId {
    if (Platform.isAndroid) return androidInterstitialId;
    if (Platform.isIOS) return iosInterstitialId;
    return androidInterstitialId;
  }

  // ---------------------------------------------------------------------------
  // 네이티브 광고 (Native)
  // ---------------------------------------------------------------------------

  /// AdMob 네이티브 광고 ID (Android).
  static const String androidNativeId = String.fromEnvironment(
    'ADMOB_ANDROID_NATIVE',
    defaultValue: 'ca-app-pub-3940256099942544/2247696110',
  );

  /// AdMob 네이티브 광고 ID (iOS).
  static const String iosNativeId = String.fromEnvironment(
    'ADMOB_IOS_NATIVE',
    defaultValue: 'ca-app-pub-3940256099942544/3986624511',
  );

  /// 플랫폼별 네이티브 광고 ID.
  static String get nativeAdUnitId {
    if (Platform.isAndroid) return androidNativeId;
    if (Platform.isIOS) return iosNativeId;
    return androidNativeId;
  }

  // ---------------------------------------------------------------------------
  // 광고 빈도 제한
  // ---------------------------------------------------------------------------

  /// 전면 광고 최소 노출 간격 (밀리초).
  static const int interstitialMinIntervalMs = 3 * 60 * 1000; // 3분
}
