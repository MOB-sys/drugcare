import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

/// 바텀 네비게이션 셸.
///
/// [StatefulNavigationShell]을 감싸서 Material 3 [NavigationBar]와
/// [IndexedStack] 기반 탭 전환을 제공한다.
class NavigationShell extends StatelessWidget {
  /// [NavigationShell] 생성자.
  ///
  /// [navigationShell] — GoRouter의 [StatefulNavigationShell].
  const NavigationShell({super.key, required this.navigationShell});

  /// GoRouter 네비게이션 셸.
  final StatefulNavigationShell navigationShell;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: navigationShell,
      bottomNavigationBar: NavigationBar(
        selectedIndex: navigationShell.currentIndex,
        onDestinationSelected: (index) {
          navigationShell.goBranch(
            index,
            initialLocation: index == navigationShell.currentIndex,
          );
        },
        backgroundColor: Theme.of(context).colorScheme.surface,
        indicatorColor: Theme.of(context).colorScheme.primaryContainer,
        height: 64,
        destinations: const [
          NavigationDestination(
            icon: Icon(Icons.home_outlined),
            selectedIcon: Icon(Icons.home),
            label: '홈',
          ),
          NavigationDestination(
            icon: Icon(Icons.medical_services_outlined),
            selectedIcon: Icon(Icons.medical_services),
            label: '복약함',
          ),
          NavigationDestination(
            icon: Icon(Icons.alarm_outlined),
            selectedIcon: Icon(Icons.alarm),
            label: '리마인더',
          ),
          NavigationDestination(
            icon: Icon(Icons.settings_outlined),
            selectedIcon: Icon(Icons.settings),
            label: '설정',
          ),
        ],
      ),
    );
  }
}
