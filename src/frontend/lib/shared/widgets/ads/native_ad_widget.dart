import 'package:flutter/material.dart';
import 'package:google_mobile_ads/google_mobile_ads.dart';

import 'package:yakmeogeo/core/constants/ad_constants.dart';

/// 네이티브 광고 위젯.
///
/// NativeAd를 로드하고 앱 디자인에 맞는 스타일로 표시한다.
/// 로드 실패 시 빈 공간([SizedBox.shrink])을 반환한다.
class NativeAdWidget extends StatefulWidget {
  /// [NativeAdWidget] 생성자.
  const NativeAdWidget({super.key});

  @override
  State<NativeAdWidget> createState() => _NativeAdWidgetState();
}

/// [NativeAdWidget]의 상태 관리 클래스.
class _NativeAdWidgetState extends State<NativeAdWidget> {
  /// 현재 로드된 네이티브 광고 인스턴스.
  NativeAd? _nativeAd;

  /// 광고 로드 완료 여부.
  bool _isLoaded = false;

  @override
  void initState() {
    super.initState();
    _loadAd();
  }

  /// 네이티브 광고를 로드한다.
  void _loadAd() {
    _nativeAd = NativeAd(
      adUnitId: AdConstants.nativeAdUnitId,
      factoryId: 'listTile',
      request: const AdRequest(),
      listener: NativeAdListener(
        onAdLoaded: (ad) {
          if (mounted) {
            setState(() => _isLoaded = true);
          }
        },
        onAdFailedToLoad: (ad, error) {
          ad.dispose();
          if (mounted) {
            setState(() {
              _nativeAd = null;
              _isLoaded = false;
            });
          }
        },
      ),
    )..load();
  }

  @override
  void dispose() {
    _nativeAd?.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    if (!_isLoaded || _nativeAd == null) {
      return const SizedBox.shrink();
    }

    return Container(
      decoration: BoxDecoration(
        color: Theme.of(context).colorScheme.surfaceContainerHighest,
        borderRadius: BorderRadius.circular(12),
      ),
      clipBehavior: Clip.antiAlias,
      constraints: const BoxConstraints(
        minHeight: 90,
        maxHeight: 120,
      ),
      child: AdWidget(ad: _nativeAd!),
    );
  }
}
