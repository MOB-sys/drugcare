import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'package:yakmeogeo/features/result/providers/interaction_provider.dart';
import 'package:yakmeogeo/features/result/widgets/interaction_result_card.dart';
import 'package:yakmeogeo/features/result/widgets/result_summary_card.dart';
import 'package:yakmeogeo/features/search/models/selected_search_item.dart';
import 'package:yakmeogeo/shared/widgets/ads/ad_banner_widget.dart';
import 'package:yakmeogeo/shared/widgets/ads/interstitial_ad_manager.dart';
import 'package:yakmeogeo/shared/widgets/common/disclaimer_banner.dart';
import 'package:yakmeogeo/shared/widgets/common/error_widget.dart';
import 'package:yakmeogeo/shared/widgets/common/loading_widget.dart';

/// 상호작용 결과 화면.
///
/// 선택된 약물/영양제 목록에 대한 상호작용 체크 결과를 표시한다.
/// 결과 요약, 개별 상호작용 카드, 면책조항, 광고 배너 순으로 배치된다.
/// 화면 진입 시 전면 광고를 표시한다 (3분 빈도 제한).
class ResultScreen extends ConsumerStatefulWidget {
  /// [ResultScreen] 생성자.
  ///
  /// [selectedItems] — 검색 화면에서 전달받은 선택 아이템 목록.
  const ResultScreen({super.key, required this.selectedItems});

  /// 선택된 아이템 목록.
  final List<SelectedSearchItem> selectedItems;

  @override
  ConsumerState<ResultScreen> createState() => _ResultScreenState();
}

class _ResultScreenState extends ConsumerState<ResultScreen> {
  @override
  void initState() {
    super.initState();
    // 결과 화면 진입 시 전면 광고 표시 시도
    InterstitialAdManager.instance.showIfReady();
  }

  @override
  Widget build(BuildContext context) {
    final resultAsync =
        ref.watch(interactionResultProvider(widget.selectedItems));

    return Scaffold(
      appBar: AppBar(
        title: const Text('상호작용 결과'),
      ),
      body: resultAsync.when(
        loading: () =>
            const LoadingWidget(message: '상호작용을 분석 중입니다...'),
        error: (error, _) => AppErrorWidget(
          message: '상호작용 확인 중 오류가 발생했습니다.\n다시 시도해 주세요.',
          onRetry: () => ref.invalidate(
              interactionResultProvider(widget.selectedItems)),
        ),
        data: (response) {
          return SingleChildScrollView(
            padding: const EdgeInsets.all(16),
            child: Column(
              children: [
                // 결과 요약 카드
                ResultSummaryCard(response: response),
                const SizedBox(height: 16),

                // 상호작용 결과 카드 목록
                if (response.results.isNotEmpty) ...[
                  ...response.results.map(
                    (result) => Padding(
                      padding: const EdgeInsets.only(bottom: 12),
                      child: InteractionResultCard(result: result),
                    ),
                  ),
                  const SizedBox(height: 8),
                ],

                // 면책조항 배너
                const DisclaimerBanner(),
                const SizedBox(height: 16),

                // 광고 배너
                const Center(child: AdBannerWidget()),
                const SizedBox(height: 16),
              ],
            ),
          );
        },
      ),
    );
  }
}
