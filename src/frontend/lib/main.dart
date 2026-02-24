import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shared_preferences/shared_preferences.dart';

import 'core/providers/device_id_provider.dart';
import 'core/router/app_router.dart';
import 'core/theme/app_theme.dart';
import 'shared/services/notification_service.dart';
import 'shared/widgets/ads/interstitial_ad_manager.dart';

/// 앱 진입점.
void main() async {
  WidgetsFlutterBinding.ensureInitialized();

  // 알림 서비스 초기화
  await NotificationService.instance.initialize();

  // 전면 광고 프리로딩
  InterstitialAdManager.instance.preload();

  final prefs = await SharedPreferences.getInstance();

  runApp(
    ProviderScope(
      overrides: [
        sharedPreferencesProvider.overrideWithValue(prefs),
      ],
      child: const YakMeogeoApp(),
    ),
  );
}

/// 약먹어 루트 위젯.
class YakMeogeoApp extends ConsumerWidget {
  /// [YakMeogeoApp] 생성자.
  const YakMeogeoApp({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final router = ref.watch(appRouterProvider);

    return MaterialApp.router(
      title: '약먹어',
      theme: AppTheme.light,
      routerConfig: router,
      debugShowCheckedModeBanner: false,
    );
  }
}
