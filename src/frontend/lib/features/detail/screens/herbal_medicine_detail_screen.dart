import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import 'package:pillright/core/theme/app_colors.dart';
import 'package:pillright/features/cabinet/models/cabinet_item.dart';
import 'package:pillright/features/cabinet/providers/cabinet_provider.dart';
import 'package:pillright/features/detail/providers/detail_provider.dart';
import 'package:pillright/features/detail/widgets/detail_cta_buttons.dart';
import 'package:pillright/features/detail/widgets/info_section.dart';
import 'package:pillright/features/search/models/herbal_medicine_detail.dart';
import 'package:pillright/features/search/models/selected_search_item.dart';
import 'package:pillright/shared/models/item_type.dart';
import 'package:pillright/core/providers/service_providers.dart';
import 'package:pillright/shared/widgets/ads/ad_banner_widget.dart';
import 'package:pillright/shared/widgets/common/disclaimer_banner.dart';

/// 한약재 상세 화면.
///
/// 한약재의 기본 정보, 효능, 용법·용량, 주의사항, 상호작용 정보를 표시한다.
class HerbalMedicineDetailScreen extends ConsumerStatefulWidget {
  /// 한약재 ID.
  final int herbalMedicineId;

  /// [HerbalMedicineDetailScreen] 생성자.
  const HerbalMedicineDetailScreen({
    super.key,
    required this.herbalMedicineId,
  });

  @override
  ConsumerState<HerbalMedicineDetailScreen> createState() =>
      _HerbalMedicineDetailScreenState();
}

/// [HerbalMedicineDetailScreen] 상태 클래스.
class _HerbalMedicineDetailScreenState
    extends ConsumerState<HerbalMedicineDetailScreen> {
  /// 복약함 추가 로딩 상태.
  bool _isAddingToCabinet = false;

  /// 메트릭스 이벤트 전송 여부.
  bool _metricsTracked = false;

  @override
  Widget build(BuildContext context) {
    final asyncDetail = ref.watch(
      herbalMedicineDetailProvider(widget.herbalMedicineId),
    );

    return Scaffold(
      appBar: AppBar(
        title: asyncDetail.when(
          data: (herbal) => Text(
            herbal.name,
            overflow: TextOverflow.ellipsis,
          ),
          loading: () => const Text('한약재 상세'),
          error: (_, __) => const Text('한약재 상세'),
        ),
      ),
      body: asyncDetail.when(
        data: (herbal) {
          // 한약재 상세 조회 메트릭스 이벤트 추적 (1회만).
          if (!_metricsTracked) {
            _metricsTracked = true;
            ref.read(metricsServiceProvider).trackEvent(
              'detail_view',
              eventData: {
                'type': 'herbal',
                'id': widget.herbalMedicineId,
              },
            );
          }
          return _buildContent(herbal);
        },
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (error, _) => _buildError(error),
      ),
    );
  }

  /// 상세 내용을 빌드한다.
  Widget _buildContent(HerbalMedicineDetail herbal) {
    return SafeArea(
      child: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // 한약재 이미지
            if (_hasContent(herbal.imageUrl))
              _buildImage(herbal.imageUrl!),

            // 기본 정보 카드
            _buildInfoCard(herbal),

            // 설명
            if (_hasContent(herbal.description))
              _buildTextSection(
                title: '설명',
                icon: Icons.eco_outlined,
                content: herbal.description!,
              ),

            // 효능
            if (_hasContent(herbal.efficacy))
              _buildTextSection(
                title: '효능',
                icon: Icons.healing_outlined,
                content: herbal.efficacy!,
              ),

            // 용법·용량
            if (_hasContent(herbal.dosage))
              _buildTextSection(
                title: '용법·용량',
                icon: Icons.medication_outlined,
                content: herbal.dosage!,
              ),

            // 주의사항
            if (_hasContent(herbal.precautions))
              _buildTextSection(
                title: '주의사항',
                icon: Icons.warning_amber_rounded,
                content: herbal.precautions!,
              ),

            // 상호작용 정보
            if (_hasContent(herbal.interactions))
              _buildTextSection(
                title: '약물 상호작용',
                icon: Icons.sync_alt_outlined,
                content: herbal.interactions!,
              ),

            // CTA 버튼
            DetailCtaButtons(
              isAddingToCabinet: _isAddingToCabinet,
              onCheckInteraction: () => _navigateToCheck(herbal),
              onAddToCabinet: () => _addToCabinet(herbal),
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

  /// 한약재 이미지를 빌드한다.
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
                  Icons.eco_outlined,
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
  Widget _buildInfoCard(HerbalMedicineDetail herbal) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final labelColor =
        isDark ? AppColors.darkTextSecondary : AppColors.textSecondary;
    final valueColor =
        isDark ? AppColors.darkTextPrimary : AppColors.textPrimary;

    final entries = <_InfoEntry>[
      if (_hasContent(herbal.koreanName))
        _InfoEntry(label: '한글명', value: herbal.koreanName!),
      if (_hasContent(herbal.latinName))
        _InfoEntry(label: '라틴명', value: herbal.latinName!),
      if (_hasContent(herbal.category))
        _InfoEntry(label: '카테고리', value: herbal.category!),
      if (_hasContent(herbal.source))
        _InfoEntry(label: '출처', value: herbal.source!),
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
              '한약재 정보를 불러오지 못했습니다.',
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
              onPressed: () => ref.invalidate(
                herbalMedicineDetailProvider(widget.herbalMedicineId),
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
  void _navigateToCheck(HerbalMedicineDetail herbal) {
    final item = SelectedSearchItem(
      itemId: herbal.id,
      name: herbal.name,
      itemType: ItemType.herbal,
    );
    context.push('/search', extra: item);
  }

  /// 복약함에 한약재를 추가한다.
  Future<void> _addToCabinet(HerbalMedicineDetail herbal) async {
    setState(() => _isAddingToCabinet = true);
    try {
      await ref.read(cabinetProvider.notifier).addItem(
            CabinetItemCreate(
              itemType: ItemType.herbal,
              itemId: herbal.id,
            ),
          );
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('${herbal.name}을(를) 복약함에 추가했습니다.'),
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
