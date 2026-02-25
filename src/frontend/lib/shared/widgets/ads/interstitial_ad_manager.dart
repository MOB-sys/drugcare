import 'package:google_mobile_ads/google_mobile_ads.dart';

import 'package:yakmeogeo/core/constants/ad_constants.dart';

/// 전면 광고 매니저 — 싱글톤.
///
/// 전면 광고 프리로딩, 빈도 제한 표시, 자동 재프리로딩을 담당한다.
class InterstitialAdManager {
  /// 싱글톤 강제용 private 생성자.
  InterstitialAdManager._();

  /// 싱글톤 인스턴스.
  static final InterstitialAdManager instance = InterstitialAdManager._();

  /// 현재 로드된 전면 광고 인스턴스.
  InterstitialAd? _interstitialAd;

  /// 광고 로드 진행 중 여부.
  bool _isLoading = false;

  /// 마지막 광고 표시 시각 (밀리초).
  int _lastShownAt = 0;

  /// 전면 광고를 프리로딩한다.
  ///
  /// 이미 로드 중이거나 로드된 광고가 있으면 무시한다.
  void preload() {
    if (_isLoading || _interstitialAd != null) return;
    _isLoading = true;

    InterstitialAd.load(
      adUnitId: AdConstants.interstitialAdUnitId,
      request: const AdRequest(),
      adLoadCallback: InterstitialAdLoadCallback(
        onAdLoaded: (ad) {
          _interstitialAd = ad;
          _isLoading = false;
          _setCallbacks(ad);
        },
        onAdFailedToLoad: (error) {
          _interstitialAd = null;
          _isLoading = false;
        },
      ),
    );
  }

  /// 광고가 준비됐고 빈도 제한을 통과하면 전면 광고를 표시한다.
  ///
  /// 로드되지 않았거나 최소 노출 간격 내이면 표시하지 않는다.
  void showIfReady() {
    if (_interstitialAd == null) return;

    final now = DateTime.now().millisecondsSinceEpoch;
    if (now - _lastShownAt < AdConstants.interstitialMinIntervalMs) return;

    _lastShownAt = now;
    _interstitialAd!.show();
    _interstitialAd = null;
  }

  /// 광고 콜백을 설정한다.
  void _setCallbacks(InterstitialAd ad) {
    ad.fullScreenContentCallback = FullScreenContentCallback(
      onAdDismissedFullScreenContent: (ad) {
        ad.dispose();
        preload();
      },
      onAdFailedToShowFullScreenContent: (ad, error) {
        ad.dispose();
        _interstitialAd = null;
        preload();
      },
    );
  }

  /// 광고 리소스를 해제한다.
  void dispose() {
    _interstitialAd?.dispose();
    _interstitialAd = null;
  }
}
