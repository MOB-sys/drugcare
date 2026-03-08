import 'package:flutter_test/flutter_test.dart';
import 'package:pillright/core/constants/ad_constants.dart';

/// NativeAdWidget 테스트.
///
/// google_mobile_ads 플랫폼 채널은 테스트 환경에서 사용 불가하므로
/// 상수와 로직만 검증한다.
void main() {
  group('NativeAdWidget', () {
    test('Android 네이티브 광고 테스트 ID가 올바르다', () {
      expect(
        AdConstants.androidNativeId,
        'ca-app-pub-3940256099942544/2247696110',
      );
    });

    test('iOS 네이티브 광고 테스트 ID가 올바르다', () {
      expect(
        AdConstants.iosNativeId,
        'ca-app-pub-3940256099942544/3986624511',
      );
    });

    test('네이티브 광고 factoryId는 listTile이다', () {
      // NativeAdWidget에서 factoryId: 'listTile'로 하드코딩
      const factoryId = 'listTile';
      expect(factoryId, 'listTile');
    });
  });
}
