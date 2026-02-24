import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'package:yakmeogeo/core/constants/app_constants.dart';
import 'package:yakmeogeo/core/theme/app_colors.dart';
import 'package:yakmeogeo/features/home/providers/home_provider.dart';
import 'package:yakmeogeo/features/home/widgets/cabinet_summary_card.dart';
import 'package:yakmeogeo/features/home/widgets/health_tip_card.dart';
import 'package:yakmeogeo/features/home/widgets/quick_search_bar.dart';
import 'package:yakmeogeo/shared/widgets/ads/native_ad_widget.dart';
import 'package:yakmeogeo/shared/widgets/common/disclaimer_banner.dart';

/// 홈 화면.
///
/// 퀵 검색 바, 복약함 요약, 건강팁, 면책조항을 표시한다.
class HomeScreen extends ConsumerWidget {
  /// [HomeScreen] 생성자.
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final cabinetAsync = ref.watch(homeCabinetSummaryProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text(AppConstants.appName),
        centerTitle: false,
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // 앱 부제
              const Text(
                AppConstants.appTagline,
                style: TextStyle(
                  fontSize: 14,
                  color: AppColors.textSecondary,
                ),
              ),
              const SizedBox(height: 20),

              // 퀵 검색 바
              const QuickSearchBar(),
              const SizedBox(height: 20),

              // 복약함 요약 카드
              cabinetAsync.when(
                data: (items) => CabinetSummaryCard(
                  itemCount: items.length,
                  onTap: () => _navigateToCabinet(context),
                ),
                loading: () => CabinetSummaryCard(
                  itemCount: 0,
                  onTap: () => _navigateToCabinet(context),
                ),
                error: (_, __) => CabinetSummaryCard(
                  itemCount: 0,
                  onTap: () => _navigateToCabinet(context),
                ),
              ),
              const SizedBox(height: 16),

              // 건강팁 카드
              const HealthTipCard(),
              const SizedBox(height: 16),

              // 네이티브 광고
              const NativeAdWidget(),
              const SizedBox(height: 16),

              // 면책조항 배너
              const DisclaimerBanner(),
            ],
          ),
        ),
      ),
    );
  }

  /// 복약함 탭으로 이동한다.
  void _navigateToCabinet(BuildContext context) {
    // 하단 네비게이션의 복약함 탭으로 전환 (인덱스 1)
    // ShellRoute 기반 네비게이션에서는 go를 사용
    // 라우터가 구성되면 context.go('/cabinet') 호출
  }
}
