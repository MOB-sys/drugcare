import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'package:pillright/features/search/models/drug_search_item.dart';
import 'package:pillright/features/search/models/selected_search_item.dart';
import 'package:pillright/features/search/models/supplement_search_item.dart';
import 'package:pillright/shared/models/item_type.dart';
import 'package:pillright/shared/models/paginated_result.dart';
import 'package:pillright/shared/widgets/common/empty_state_widget.dart';
import 'package:pillright/shared/widgets/common/error_widget.dart';
import 'package:pillright/shared/widgets/common/loading_widget.dart';
import 'package:pillright/shared/widgets/common/search_item_card.dart';

/// 검색 결과 통합 리스트 위젯.
///
/// 약물과 영양제 검색 결과를 하나의 스크롤 리스트로 합쳐서 표시한다.
/// 각 데이터 소스의 로딩/에러/빈 상태를 처리한다.
class SearchResultList extends StatelessWidget {
  /// [SearchResultList] 생성자.
  ///
  /// [drugResults] — 약물 검색 결과 (AsyncValue).
  /// [supplementResults] — 영양제 검색 결과 (AsyncValue).
  /// [selectedItems] — 현재 선택된 아이템 목록.
  /// [onItemTap] — 아이템 선택/해제 콜백.
  /// [onRetry] — 에러 시 재시도 콜백.
  const SearchResultList({
    super.key,
    required this.drugResults,
    required this.supplementResults,
    required this.selectedItems,
    required this.onItemTap,
    required this.onRetry,
  });

  /// 약물 검색 결과.
  final AsyncValue<PaginatedResult<DrugSearchItem>?> drugResults;

  /// 영양제 검색 결과.
  final AsyncValue<PaginatedResult<SupplementSearchItem>?> supplementResults;

  /// 현재 선택된 아이템 목록.
  final List<SelectedSearchItem> selectedItems;

  /// 아이템 선택/해제 콜백.
  final ValueChanged<SelectedSearchItem> onItemTap;

  /// 에러 시 재시도 콜백.
  final VoidCallback onRetry;

  /// 아이템이 선택되었는지 확인한다.
  bool _isSelected(ItemType type, int id) {
    return selectedItems.any(
      (e) => e.itemType == type && e.itemId == id,
    );
  }

  @override
  Widget build(BuildContext context) {
    // 둘 다 로딩 중
    final drugLoading = drugResults is AsyncLoading;
    final suppLoading = supplementResults is AsyncLoading;
    if (drugLoading && suppLoading) {
      return const LoadingWidget(message: '검색 중...');
    }

    // 에러 처리 (둘 다 에러면 에러 표시)
    final drugError = drugResults is AsyncError;
    final suppError = supplementResults is AsyncError;
    if (drugError && suppError) {
      return AppErrorWidget(
        message: '검색 중 오류가 발생했습니다.',
        onRetry: onRetry,
      );
    }

    // 결과 합치기
    final List<Widget> cards = [];

    // 약물 결과
    drugResults.when(
      data: (result) {
        if (result != null) {
          for (final drug in result.items) {
            cards.add(
              SearchItemCard(
                name: drug.itemName,
                subtitle: drug.entpName,
                itemType: ItemType.drug,
                isSelected: _isSelected(ItemType.drug, drug.id),
                onTap: () => onItemTap(
                  SelectedSearchItem(
                    itemType: ItemType.drug,
                    itemId: drug.id,
                    name: drug.itemName,
                  ),
                ),
              ),
            );
          }
        }
      },
      loading: () {
        cards.add(const Padding(
          padding: EdgeInsets.symmetric(vertical: 16),
          child: LoadingWidget(message: '약물 검색 중...'),
        ));
      },
      error: (e, _) {
        cards.add(
          Padding(
            padding: const EdgeInsets.symmetric(vertical: 16),
            child: AppErrorWidget(
              message: '약물 검색 중 오류가 발생했습니다.',
              onRetry: onRetry,
            ),
          ),
        );
      },
    );

    // 영양제 결과
    supplementResults.when(
      data: (result) {
        if (result != null) {
          for (final supp in result.items) {
            cards.add(
              SearchItemCard(
                name: supp.productName,
                subtitle: supp.company ?? supp.mainIngredient,
                itemType: ItemType.supplement,
                isSelected: _isSelected(ItemType.supplement, supp.id),
                onTap: () => onItemTap(
                  SelectedSearchItem(
                    itemType: ItemType.supplement,
                    itemId: supp.id,
                    name: supp.productName,
                  ),
                ),
              ),
            );
          }
        }
      },
      loading: () {
        cards.add(const Padding(
          padding: EdgeInsets.symmetric(vertical: 16),
          child: LoadingWidget(message: '영양제 검색 중...'),
        ));
      },
      error: (e, _) {
        cards.add(
          Padding(
            padding: const EdgeInsets.symmetric(vertical: 16),
            child: AppErrorWidget(
              message: '영양제 검색 중 오류가 발생했습니다.',
              onRetry: onRetry,
            ),
          ),
        );
      },
    );

    // 결과 없음
    if (cards.isEmpty) {
      return const EmptyStateWidget(
        message: '검색 결과가 없습니다.\n다른 이름으로 검색해 보세요.',
        icon: Icons.search_off,
      );
    }

    return ListView.separated(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      itemCount: cards.length,
      separatorBuilder: (_, __) => const SizedBox(height: 4),
      itemBuilder: (_, index) => cards[index],
    );
  }
}
