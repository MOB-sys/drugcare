import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import 'package:pillright/core/theme/app_colors.dart';
import 'package:pillright/features/cabinet/models/cabinet_item.dart';
import 'package:pillright/features/cabinet/providers/cabinet_provider.dart';
import 'package:pillright/features/detail/providers/detail_provider.dart';
import 'package:pillright/features/detail/widgets/detail_cta_buttons.dart';
import 'package:pillright/features/detail/widgets/dur_safety_section.dart';
import 'package:pillright/features/detail/widgets/info_section.dart';
import 'package:pillright/features/detail/widgets/ingredients_table.dart';
import 'package:pillright/features/detail/widgets/pregnancy_safety_section.dart';
import 'package:pillright/features/detail/widgets/structured_side_effects.dart';
import 'package:pillright/features/search/models/drug_detail.dart';
import 'package:pillright/features/search/models/selected_search_item.dart';
import 'package:pillright/shared/models/item_type.dart';
import 'package:pillright/core/providers/service_providers.dart';
import 'package:pillright/shared/services/share_service.dart';
import 'package:pillright/shared/widgets/ads/ad_banner_widget.dart';
import 'package:pillright/shared/widgets/common/disclaimer_banner.dart';

/// 약물 상세 화면.
///
/// 약물의 기본 정보, 효능·효과, 용법·용량, 성분, DUR 안전성,
/// 부작용, 주의사항, 식품 상호작용, 보관법을 표시한다.
class DrugDetailScreen extends ConsumerStatefulWidget {
  /// 약물 ID.
  final int drugId;

  /// [DrugDetailScreen] 생성자.
  const DrugDetailScreen({super.key, required this.drugId});

  @override
  ConsumerState<DrugDetailScreen> createState() => _DrugDetailScreenState();
}

/// [DrugDetailScreen] 상태 클래스.
class _DrugDetailScreenState extends ConsumerState<DrugDetailScreen> {
  /// 복약함 추가 로딩 상태.
  bool _isAddingToCabinet = false;

  /// 메트릭스 이벤트 전송 여부.
  bool _metricsTracked = false;

  @override
  Widget build(BuildContext context) {
    final asyncDetail = ref.watch(drugDetailProvider(widget.drugId));

    return Scaffold(
      appBar: AppBar(
        title: asyncDetail.when(
          data: (drug) => Text(
            drug.itemName,
            overflow: TextOverflow.ellipsis,
          ),
          loading: () => const Text('약물 상세'),
          error: (_, __) => const Text('약물 상세'),
        ),
        actions: [
          if (asyncDetail.hasValue)
            IconButton(
              icon: const Icon(Icons.share),
              tooltip: '공유',
              onPressed: () {
                final drug = asyncDetail.value!;
                ShareService.shareDrugInfo(
                  name: drug.itemName,
                  type: 'drug',
                  id: drug.id,
                );
              },
            ),
        ],
      ),
      body: asyncDetail.when(
        data: (drug) {
          // 약물 상세 조회 메트릭스 이벤트 추적 (1회만).
          if (!_metricsTracked) {
            _metricsTracked = true;
            ref.read(metricsServiceProvider).trackEvent(
              'detail_view',
              eventData: {'type': 'drug', 'id': widget.drugId},
            );
          }
          return _buildContent(drug);
        },
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (error, _) => _buildError(error),
      ),
    );
  }

  /// 상세 내용을 빌드한다.
  Widget _buildContent(DrugDetail drug) {
    return SafeArea(
      child: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // 약물 이미지
            if (drug.itemImage != null && drug.itemImage!.isNotEmpty)
              _buildImage(drug.itemImage!),

            // 기본 정보 카드
            _buildInfoCard(drug),

            // 효능효과
            if (_hasContent(drug.efcyQesitm))
              _buildTextSection(
                title: '효능·효과',
                icon: Icons.healing_outlined,
                content: drug.efcyQesitm!,
              ),

            // 용법용량
            if (_hasContent(drug.useMethodQesitm))
              _buildTextSection(
                title: '용법·용량',
                icon: Icons.medication_outlined,
                content: drug.useMethodQesitm!,
              ),

            // 성분 테이블
            if (drug.ingredients != null && drug.ingredients!.isNotEmpty)
              IngredientsTable(ingredients: drug.ingredients!),

            // DUR 안전성 정보
            if (drug.durSafety != null && drug.durSafety!.isNotEmpty)
              DURSafetySection(items: drug.durSafety!),

            // 임신·수유 안전정보
            if (PregnancySafetySection.shouldShow(
              durSafety: drug.durSafety,
              atpnQesitm: drug.atpnQesitm,
              atpnWarnQesitm: drug.atpnWarnQesitm,
            ))
              Builder(builder: (_) {
                final data = PregnancySafetySection.extractData(
                  durSafety: drug.durSafety,
                  atpnQesitm: drug.atpnQesitm,
                  atpnWarnQesitm: drug.atpnWarnQesitm,
                );
                return PregnancySafetySection(
                  pregnancyItems: data.pregnancyItems,
                  breastfeedingSentences: data.breastfeedingSentences,
                  pregnancyCautionSentences: data.pregnancyCautionSentences,
                );
              }),

            // 부작용 (구조화)
            if (_hasContent(drug.seQesitm))
              StructuredSideEffects(sideEffectsText: drug.seQesitm!),

            // 주의사항 경고
            if (_hasContent(drug.atpnWarnQesitm))
              _buildTextSection(
                title: '주의사항 (경고)',
                icon: Icons.warning_amber_rounded,
                content: drug.atpnWarnQesitm!,
              ),

            // 주의사항
            if (_hasContent(drug.atpnQesitm))
              _buildTextSection(
                title: '주의사항',
                icon: Icons.info_outline,
                content: drug.atpnQesitm!,
              ),

            // 식품 상호작용
            if (_hasContent(drug.intrcQesitm))
              _buildTextSection(
                title: '음식물 상호작용',
                icon: Icons.restaurant_outlined,
                content: drug.intrcQesitm!,
              ),

            // 보관법
            if (_hasContent(drug.depositMethodQesitm))
              _buildTextSection(
                title: '보관법',
                icon: Icons.inventory_2_outlined,
                content: drug.depositMethodQesitm!,
              ),

            // CTA 버튼
            DetailCtaButtons(
              isAddingToCabinet: _isAddingToCabinet,
              onCheckInteraction: () => _navigateToCheck(drug),
              onAddToCabinet: () => _addToCabinet(drug),
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

  /// 약물 이미지를 빌드한다.
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
                  Icons.medication_outlined,
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
  Widget _buildInfoCard(DrugDetail drug) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final labelColor =
        isDark ? AppColors.darkTextSecondary : AppColors.textSecondary;
    final valueColor =
        isDark ? AppColors.darkTextPrimary : AppColors.textPrimary;

    final entries = <_InfoEntry>[
      if (_hasContent(drug.entpName))
        _InfoEntry(label: '업체명', value: drug.entpName!),
      if (_hasContent(drug.classNo))
        _InfoEntry(label: '분류번호', value: drug.classNo!),
      if (_hasContent(drug.etcOtcCode))
        _InfoEntry(
          label: '구분',
          value: drug.etcOtcCode == '전문의약품' ? '전문의약품' : '일반의약품',
        ),
      if (_hasContent(drug.chart))
        _InfoEntry(label: '성상', value: drug.chart!),
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
              '약물 정보를 불러오지 못했습니다.',
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
                  ref.invalidate(drugDetailProvider(widget.drugId)),
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
  void _navigateToCheck(DrugDetail drug) {
    final item = SelectedSearchItem(
      itemId: drug.id,
      name: drug.itemName,
      itemType: ItemType.drug,
    );
    context.push('/search', extra: item);
  }

  /// 복약함에 약물을 추가한다.
  Future<void> _addToCabinet(DrugDetail drug) async {
    setState(() => _isAddingToCabinet = true);
    try {
      await ref.read(cabinetProvider.notifier).addItem(
            CabinetItemCreate(
              itemType: ItemType.drug,
              itemId: drug.id,
            ),
          );
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('${drug.itemName}을(를) 복약함에 추가했습니다.'),
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
