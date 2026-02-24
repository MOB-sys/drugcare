import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shared_preferences/shared_preferences.dart';

import 'core/providers/device_id_provider.dart';
import 'core/router/app_router.dart';
import 'core/theme/app_theme.dart';

/// 앱 진입점.
void main() async {
  WidgetsFlutterBinding.ensureInitialized();

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
