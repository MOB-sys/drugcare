import 'package:flutter_test/flutter_test.dart';
import 'package:yakmeogeo/core/constants/ad_constants.dart';

void main() {
  group('InterstitialAdManager', () {
    test('빈도 제한 상수가 3분(180000ms)이다', () {
      expect(AdConstants.interstitialMinIntervalMs, 3 * 60 * 1000);
    });

    test('빈도 제한 로직: 3분 이내면 표시하지 않는다', () {
      var lastShownAt = 0;
      final now = DateTime.now().millisecondsSinceEpoch;

      // 첫 번째 호출: 표시됨
      lastShownAt = 0;
      final shouldShow1 =
          now - lastShownAt >= AdConstants.interstitialMinIntervalMs;
      expect(shouldShow1, true);

      // 두 번째 호출: 1분 후 → 표시 안 됨
      lastShownAt = now;
      final oneMinuteLater = now + 60 * 1000;
      final shouldShow2 =
          oneMinuteLater - lastShownAt >= AdConstants.interstitialMinIntervalMs;
      expect(shouldShow2, false);

      // 세 번째 호출: 3분 후 → 표시됨
      final threeMinutesLater = now + 3 * 60 * 1000;
      final shouldShow3 = threeMinutesLater - lastShownAt >=
          AdConstants.interstitialMinIntervalMs;
      expect(shouldShow3, true);
    });

    test('Android 전면 광고 테스트 ID가 올바르다', () {
      expect(
        AdConstants.androidInterstitialId,
        'ca-app-pub-3940256099942544/1033173712',
      );
    });

    test('iOS 전면 광고 테스트 ID가 올바르다', () {
      expect(
        AdConstants.iosInterstitialId,
        'ca-app-pub-3940256099942544/4411468910',
      );
    });
  });
}
