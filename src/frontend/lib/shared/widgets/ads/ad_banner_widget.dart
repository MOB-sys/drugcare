import 'package:flutter/material.dart';
import 'package:google_mobile_ads/google_mobile_ads.dart';

import 'package:pillright/core/constants/ad_constants.dart';

/// AdMob 배너 광고 래퍼 위젯.
///
/// 320×50 표준 배너 광고를 로드하고 표시한다.
/// 로드 실패 시 빈 공간([SizedBox.shrink])을 반환한다.
class AdBannerWidget extends StatefulWidget {
  /// [AdBannerWidget] 생성자.
  const AdBannerWidget({super.key});

  @override
  State<AdBannerWidget> createState() => _AdBannerWidgetState();
}

/// [AdBannerWidget]의 상태 관리 클래스.
class _AdBannerWidgetState extends State<AdBannerWidget> {
  /// 현재 로드된 배너 광고 인스턴스.
  BannerAd? _bannerAd;

  /// 광고 로드 완료 여부.
  bool _isLoaded = false;

  @override
  void initState() {
    super.initState();
    _loadAd();
  }

  /// 배너 광고를 로드한다.
  void _loadAd() {
    _bannerAd = BannerAd(
      adUnitId: AdConstants.bannerAdUnitId,
      size: AdSize.banner,
      request: const AdRequest(),
      listener: BannerAdListener(
        onAdLoaded: (ad) {
          if (mounted) {
            setState(() => _isLoaded = true);
          }
        },
        onAdFailedToLoad: (ad, error) {
          ad.dispose();
          if (mounted) {
            setState(() {
              _bannerAd = null;
              _isLoaded = false;
            });
          }
        },
      ),
    )..load();
  }

  @override
  void dispose() {
    _bannerAd?.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    if (!_isLoaded || _bannerAd == null) {
      return const SizedBox.shrink();
    }

    return SizedBox(
      width: 320,
      height: 50,
      child: AdWidget(ad: _bannerAd!),
    );
  }
}
