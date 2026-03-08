import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import 'package:pillright/core/router/navigation_shell.dart';
import 'package:pillright/features/cabinet/screens/cabinet_screen.dart';
import 'package:pillright/features/home/screens/home_screen.dart';
import 'package:pillright/features/reminder/models/reminder.dart';
import 'package:pillright/features/reminder/screens/reminder_form_screen.dart';
import 'package:pillright/features/reminder/screens/reminder_screen.dart';
import 'package:pillright/features/result/screens/result_screen.dart';
import 'package:pillright/features/search/models/selected_search_item.dart';
import 'package:pillright/features/search/screens/search_screen.dart';
import 'package:pillright/features/settings/screens/feedback_screen.dart';
import 'package:pillright/features/settings/screens/legal_screen.dart';
import 'package:pillright/features/settings/screens/settings_screen.dart';

/// 루트 네비게이터 키.
final _rootNavigatorKey = GlobalKey<NavigatorState>();

/// 홈 탭 네비게이터 키.
final _homeNavigatorKey = GlobalKey<NavigatorState>(debugLabel: 'home');

/// 복약함 탭 네비게이터 키.
final _cabinetNavigatorKey = GlobalKey<NavigatorState>(debugLabel: 'cabinet');

/// 리마인더 탭 네비게이터 키.
final _reminderNavigatorKey = GlobalKey<NavigatorState>(debugLabel: 'reminder');

/// 설정 탭 네비게이터 키.
final _settingsNavigatorKey =
    GlobalKey<NavigatorState>(debugLabel: 'settings');

/// GoRouter 프로바이더.
///
/// [StatefulShellRoute.indexedStack]을 사용하여 바텀 네비게이션과
/// 풀스크린 라우트를 분리한다.
final appRouterProvider = Provider<GoRouter>((ref) {
  return GoRouter(
    navigatorKey: _rootNavigatorKey,
    initialLocation: '/home',
    routes: [
      // ── 바텀 네비게이션 (탭 유지) ──
      StatefulShellRoute.indexedStack(
        builder: (context, state, navigationShell) {
          return NavigationShell(navigationShell: navigationShell);
        },
        branches: [
          StatefulShellBranch(
            navigatorKey: _homeNavigatorKey,
            routes: [
              GoRoute(
                path: '/home',
                builder: (context, state) => const HomeScreen(),
              ),
            ],
          ),
          StatefulShellBranch(
            navigatorKey: _cabinetNavigatorKey,
            routes: [
              GoRoute(
                path: '/cabinet',
                builder: (context, state) => const CabinetScreen(),
              ),
            ],
          ),
          StatefulShellBranch(
            navigatorKey: _reminderNavigatorKey,
            routes: [
              GoRoute(
                path: '/reminder',
                builder: (context, state) => const ReminderScreen(),
              ),
            ],
          ),
          StatefulShellBranch(
            navigatorKey: _settingsNavigatorKey,
            routes: [
              GoRoute(
                path: '/settings',
                builder: (context, state) => const SettingsScreen(),
              ),
            ],
          ),
        ],
      ),

      // ── 풀스크린 라우트 (바텀 네비게이션 없음) ──
      GoRoute(
        parentNavigatorKey: _rootNavigatorKey,
        path: '/search',
        builder: (context, state) => const SearchScreen(),
      ),
      GoRoute(
        parentNavigatorKey: _rootNavigatorKey,
        path: '/result',
        builder: (context, state) {
          final items = state.extra as List<SelectedSearchItem>? ?? const [];
          return ResultScreen(selectedItems: items);
        },
      ),
      GoRoute(
        parentNavigatorKey: _rootNavigatorKey,
        path: '/reminder/form',
        builder: (context, state) {
          final reminder = state.extra as Reminder?;
          return ReminderFormScreen(existingReminder: reminder);
        },
      ),
      GoRoute(
        parentNavigatorKey: _rootNavigatorKey,
        path: '/settings/legal',
        builder: (context, state) {
          final type = state.uri.queryParameters['type'] ?? 'terms';
          return LegalScreen(type: type);
        },
      ),
      GoRoute(
        parentNavigatorKey: _rootNavigatorKey,
        path: '/settings/feedback',
        builder: (context, state) => const FeedbackScreen(),
      ),
    ],
  );
});
