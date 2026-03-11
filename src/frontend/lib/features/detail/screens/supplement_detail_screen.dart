import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import 'package:pillright/core/theme/app_colors.dart';
import 'package:pillright/features/cabinet/models/cabinet_item.dart';
import 'package:pillright/features/cabinet/providers/cabinet_provider.dart';
import 'package:pillright/features/detail/providers/detail_provider.dart';
import 'package:pillright/features/detail/widgets/detail_cta_buttons.dart';
import 'package:pillright/features/detail/widgets/info_section.dart';
import 'package:pillright/features/detail/widgets/ingredients_table.dart';
import 'package:pillright/features/search/models/selected_search_item.dart';
import 'package:pillright/features/search/models/supplement_detail.dart';
import 'package:pillright/shared/models/item_type.dart';
import 'package:pillright/core/providers/service_providers.dart';
import 'package:pillright/shared/services/share_service.dart';
import 'package:pillright/shared/widgets/ads/ad_banner_widget.dart';
import 'package:pillright/shared/widgets/common/disclaimer_banner.dart';

/// 영양제 상세 화면.
///
/// 영양제의 기본 정보, 기능성, 성분, 섭취방법, 주의사항을 표시한다.
class SupplementDetailScreen extends ConsumerStatefulWidget {
  /// 영양제 ID.
  final int supplementId;

  /// [SupplementDetailScreen] 생성자.
  const SupplementDetailScreen({super.key, required this.supplementId});

  @override
  ConsumerState<SupplementDetailScreen> createState() =>
      _SupplementDetailScreenState();
}

/// [SupplementDetailScreen] 상태 클래스.
class _SupplementDetailScreenState
    extends ConsumerState<SupplementDetailScreen> {
  /// 복약함 추가 로딩 상태.
  bool _isAddingToCabinet = false;

  @override
  Widget build(BuildContext context) {
    final asyncDetail =
        ref.watch(supplementDetailProvider(widget.supplementId));

    return Scaffold(
      appBar: AppBar(
        title: asyncDetail.when(
          data: (supplement) => Text(
            supplement.productName,
            overflow: TextOverflow.ellipsis,
          ),
          loading: () => const Text('영양제 상세'),
          error: (_, __) => const Text('영양제 상세'),
        ),
        actions: [
          if (asyncDetail.hasValue)
            IconButton(
              icon: const Icon(Icons.share),
              tooltip: '공유',
              onPressed: () {
                final supplement = asyncDetail.value!;
                ShareService.shareDrugInfo(
                  name: supplement.productName,
                  type: 'supplement',
                  id: supplement.id,
                );
              },
            ),
        ],
      ),
      body: asyncDetail.when(
        data: (supplement) {
          // 영양제 상세 조회 메트릭스 이벤트 추적 (fire-and-forget).
          ref.read(metricsServiceProvider).trackEvent(
            'detail_view',
            eventData: {'type': 'supplement', 'id': widget.supplementId},
          );
          return _buildContent(supplement);
        },
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (error, _) => _buildError(error),
      ),
    );
  }

  /// 상세 내용을 빌드한다.
  Widget _buildContent(SupplementDetail supplement) {
    return SafeArea(
      child: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // 기본 정보 카드
            _buildInfoCard(supplement),

            // 기능성
            if (_hasContent(supplement.functionality))
              _buildTextSection(
                title: '기능성',
                icon: Icons.star_outline,
                content: supplement.functionality!,
              ),

            // 성분 테이블
            if (supplement.ingredients != null &&
                supplement.ingredients!.isNotEmpty)
              SupplementIngredientsTable(
                ingredients: supplement.ingredients!,
              ),

            // 섭취방법
            if (_hasContent(supplement.intakeMethod))
              _buildTextSection(
                title: '섭취방법',
                icon: Icons.schedule_outlined,
                content: supplement.intakeMethod!,
              ),

            // 주의사항
            if (_hasContent(supplement.precautions))
              _buildTextSection(
                title: '주의사항',
                icon: Icons.warning_amber_rounded,
                content: supplement.precautions!,
              ),

            // 카테고리
            if (_hasContent(supplement.category))
              _buildTextSection(
                title: '카테고리',
                icon: Icons.category_outlined,
                content: supplement.category!,
              ),

            // CTA 버튼
            DetailCtaButtons(
              isAddingToCabinet: _isAddingToCabinet,
              onCheckInteraction: () => _navigateToCheck(supplement),
              onAddToCabinet: () => _addToCabinet(supplement),
            ),
            const SizedBox(height: 12),

            // 배너 광고
            const Center(child: AdBannerWidget()),
            const SizedBox(height: 12),

            // 면책조항
            const DisclaimerBanner(),
          ],
        ),
      ),
    );
  }

  /// 기본 정보 카드를 빌드한다.
  Widget _buildInfoCard(SupplementDetail supplement) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final labelColor =
        isDark ? AppColors.darkTextSecondary : AppColors.textSecondary;
    final valueColor =
        isDark ? AppColors.darkTextPrimary : AppColors.textPrimary;

    final entries = <_InfoEntry>[
      if (_hasContent(supplement.company))
        _InfoEntry(label: '제조사', value: supplement.company!),
      if (_hasContent(supplement.registrationNo))
        _InfoEntry(label: '신고번호', value: supplement.registrationNo!),
      if (_hasContent(supplement.mainIngredient))
        _InfoEntry(label: '주성분', value: supplement.mainIngredient!),
      if (_hasContent(supplement.source))
        _InfoEntry(label: '출처', value: supplement.source!),
    ];

    if (entries.isEmpty) return const SizedBox.shrink();

    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: entries.map((entry) {
            return Padding(
              padding: const EdgeInsets.symmetric(vertical: 4),
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  SizedBox(
                    width: 80,
                    child: Text(
                      entry.label,
                      style: TextStyle(
                        fontSize: 13,
                        color: labelColor,
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: SelectableText(
                      entry.value,
                      style: TextStyle(fontSize: 13, color: valueColor),
                    ),
                  ),
                ],
              ),
            );
          }).toList(),
        ),
      ),
    );
  }

  /// 텍스트 기반 정보 섹션을 빌드한다.
  Widget _buildTextSection({
    required String title,
    required IconData icon,
    required String content,
  }) {
    return InfoSection(
      title: title,
      icon: icon,
      child: SelectableText(
        content,
        style: TextStyle(
          fontSize: 14,
          height: 1.6,
          color: Theme.of(context).brightness == Brightness.dark
              ? AppColors.darkTextPrimary
              : AppColors.textPrimary,
        ),
      ),
    );
  }

  /// 에러 화면을 빌드한다.
  Widget _buildError(Object error) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(
              Icons.error_outline,
              size: 48,
              color: AppColors.danger,
            ),
            const SizedBox(height: 16),
            Text(
              '영양제 정보를 불러오지 못했습니다.',
              style: TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.w600,
                color: Theme.of(context).brightness == Brightness.dark
                    ? AppColors.darkTextPrimary
                    : AppColors.textPrimary,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              error.toString(),
              textAlign: TextAlign.center,
              style: TextStyle(
                fontSize: 13,
                color: Theme.of(context).brightness == Brightness.dark
                    ? AppColors.darkTextSecondary
                    : AppColors.textSecondary,
              ),
            ),
            const SizedBox(height: 24),
            FilledButton.icon(
              onPressed: () => ref.invalidate(
                supplementDetailProvider(widget.supplementId),
              ),
              icon: const Icon(Icons.refresh),
              label: const Text('다시 시도'),
            ),
          ],
        ),
      ),
    );
  }

  /// 문자열이 비어있지 않은지 확인한다.
  bool _hasContent(String? value) {
    return value != null && value.trim().isNotEmpty;
  }

  /// 상호작용 체크 화면으로 이동한다.
  void _navigateToCheck(SupplementDetail supplement) {
    final item = SelectedSearchItem(
      itemId: supplement.id,
      name: supplement.productName,
      itemType: ItemType.supplement,
    );
    context.push('/search', extra: item);
  }

  /// 복약함에 영양제를 추가한다.
  Future<void> _addToCabinet(SupplementDetail supplement) async {
    setState(() => _isAddingToCabinet = true);
    try {
      await ref.read(cabinetProvider.notifier).addItem(
            CabinetItemCreate(
              itemType: ItemType.supplement,
              itemId: supplement.id,
            ),
          );
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('${supplement.productName}을(를) 복약함에 추가했습니다.'),
            behavior: SnackBarBehavior.floating,
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(8),
            ),
          ),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: const Text('복약함 추가에 실패했습니다.'),
            backgroundColor: AppColors.danger,
            behavior: SnackBarBehavior.floating,
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(8),
            ),
          ),
        );
      }
    } finally {
      if (mounted) {
        setState(() => _isAddingToCabinet = false);
      }
    }
  }
}

/// 정보 카드의 라벨-값 쌍.
class _InfoEntry {
  /// 라벨.
  final String label;

  /// 값.
  final String value;

  /// [_InfoEntry] 생성자.
  const _InfoEntry({required this.label, required this.value});
}
