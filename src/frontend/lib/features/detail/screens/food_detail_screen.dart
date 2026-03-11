import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import 'package:pillright/core/theme/app_colors.dart';
import 'package:pillright/features/cabinet/models/cabinet_item.dart';
import 'package:pillright/features/cabinet/providers/cabinet_provider.dart';
import 'package:pillright/features/detail/providers/detail_provider.dart';
import 'package:pillright/features/detail/widgets/detail_cta_buttons.dart';
import 'package:pillright/features/detail/widgets/info_section.dart';
import 'package:pillright/features/search/models/food_detail.dart';
import 'package:pillright/features/search/models/selected_search_item.dart';
import 'package:pillright/shared/models/item_type.dart';
import 'package:pillright/core/providers/service_providers.dart';
import 'package:pillright/shared/widgets/ads/ad_banner_widget.dart';
import 'package:pillright/shared/widgets/common/disclaimer_banner.dart';

/// 식품 상세 화면.
///
/// 식품의 기본 정보, 설명, 영양 성분, 주의사항, 상호작용 정보를 표시한다.
class FoodDetailScreen extends ConsumerStatefulWidget {
  /// 식품 ID.
  final int foodId;

  /// [FoodDetailScreen] 생성자.
  const FoodDetailScreen({super.key, required this.foodId});

  @override
  ConsumerState<FoodDetailScreen> createState() => _FoodDetailScreenState();
}

/// [FoodDetailScreen] 상태 클래스.
class _FoodDetailScreenState extends ConsumerState<FoodDetailScreen> {
  /// 복약함 추가 로딩 상태.
  bool _isAddingToCabinet = false;

  /// 메트릭스 이벤트 전송 여부.
  bool _metricsTracked = false;

  @override
  Widget build(BuildContext context) {
    final asyncDetail = ref.watch(foodDetailProvider(widget.foodId));

    return Scaffold(
      appBar: AppBar(
        title: asyncDetail.when(
          data: (food) => Text(
            food.name,
            overflow: TextOverflow.ellipsis,
          ),
          loading: () => const Text('식품 상세'),
          error: (_, __) => const Text('식품 상세'),
        ),
      ),
      body: asyncDetail.when(
        data: (food) {
          // 식품 상세 조회 메트릭스 이벤트 추적 (1회만).
          if (!_metricsTracked) {
            _metricsTracked = true;
            ref.read(metricsServiceProvider).trackEvent(
              'detail_view',
              eventData: {'type': 'food', 'id': widget.foodId},
            );
          }
          return _buildContent(food);
        },
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (error, _) => _buildError(error),
      ),
    );
  }

  /// 상세 내용을 빌드한다.
  Widget _buildContent(FoodDetail food) {
    return SafeArea(
      child: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // 식품 이미지
            if (_hasContent(food.imageUrl))
              _buildImage(food.imageUrl!),

            // 기본 정보 카드
            _buildInfoCard(food),

            // 설명
            if (_hasContent(food.description))
              _buildTextSection(
                title: '설명',
                icon: Icons.restaurant_outlined,
                content: food.description!,
              ),

            // 일반명
            if (food.commonNames != null && food.commonNames!.isNotEmpty)
              _buildTextSection(
                title: '일반명',
                icon: Icons.label_outline,
                content: food.commonNames!.join(', '),
              ),

            // 영양 성분
            if (_hasContent(food.nutrients))
              _buildTextSection(
                title: '영양 성분',
                icon: Icons.eco_outlined,
                content: food.nutrients!,
              ),

            // 주의사항
            if (_hasContent(food.precautions))
              _buildTextSection(
                title: '주의사항',
                icon: Icons.warning_amber_rounded,
                content: food.precautions!,
              ),

            // 상호작용 정보
            if (_hasContent(food.interactions))
              _buildTextSection(
                title: '약물 상호작용',
                icon: Icons.sync_alt_outlined,
                content: food.interactions!,
              ),

            // CTA 버튼
            DetailCtaButtons(
              isAddingToCabinet: _isAddingToCabinet,
              onCheckInteraction: () => _navigateToCheck(food),
              onAddToCabinet: () => _addToCabinet(food),
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

  /// 식품 이미지를 빌드한다.
  Widget _buildImage(String imageUrl) {
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      clipBehavior: Clip.antiAlias,
      child: AspectRatio(
        aspectRatio: 16 / 9,
        child: Image.network(
          imageUrl,
          fit: BoxFit.contain,
          errorBuilder: (context, error, stackTrace) {
            return Container(
              color: Theme.of(context).brightness == Brightness.dark
                  ? AppColors.darkSurface
                  : AppColors.primaryLight,
              child: Center(
                child: Icon(
                  Icons.restaurant_outlined,
                  size: 48,
                  color: Theme.of(context).brightness == Brightness.dark
                      ? AppColors.darkTextSecondary
                      : AppColors.textSecondary,
                ),
              ),
            );
          },
          loadingBuilder: (context, child, loadingProgress) {
            if (loadingProgress == null) return child;
            return Container(
              color: Theme.of(context).brightness == Brightness.dark
                  ? AppColors.darkSurface
                  : AppColors.primaryLight,
              child: const Center(child: CircularProgressIndicator()),
            );
          },
        ),
      ),
    );
  }

  /// 기본 정보 카드를 빌드한다.
  Widget _buildInfoCard(FoodDetail food) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final labelColor =
        isDark ? AppColors.darkTextSecondary : AppColors.textSecondary;
    final valueColor =
        isDark ? AppColors.darkTextPrimary : AppColors.textPrimary;

    final entries = <_InfoEntry>[
      if (_hasContent(food.category))
        _InfoEntry(label: '카테고리', value: food.category!),
      if (_hasContent(food.source))
        _InfoEntry(label: '출처', value: food.source!),
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
              '식품 정보를 불러오지 못했습니다.',
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
              '네트워크 연결을 확인하고 다시 시도해 주세요.',
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
              onPressed: () =>
                  ref.invalidate(foodDetailProvider(widget.foodId)),
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
  void _navigateToCheck(FoodDetail food) {
    final item = SelectedSearchItem(
      itemId: food.id,
      name: food.name,
      itemType: ItemType.food,
    );
    context.push('/search', extra: item);
  }

  /// 복약함에 식품을 추가한다.
  Future<void> _addToCabinet(FoodDetail food) async {
    setState(() => _isAddingToCabinet = true);
    try {
      await ref.read(cabinetProvider.notifier).addItem(
            CabinetItemCreate(
              itemType: ItemType.food,
              itemId: food.id,
            ),
          );
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('${food.name}을(를) 복약함에 추가했습니다.'),
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
