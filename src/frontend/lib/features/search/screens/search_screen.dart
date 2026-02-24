import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import 'package:yakmeogeo/core/constants/app_constants.dart';
import 'package:yakmeogeo/core/theme/app_colors.dart';
import 'package:yakmeogeo/features/search/providers/search_provider.dart';
import 'package:yakmeogeo/features/search/widgets/search_result_list.dart';
import 'package:yakmeogeo/features/search/widgets/selected_items_bar.dart';
import 'package:yakmeogeo/shared/models/item_type.dart';
import 'package:yakmeogeo/shared/widgets/common/empty_state_widget.dart';

/// 약물/영양제 통합 검색 화면.
///
/// 사용자가 약물·영양제를 검색하고 선택한 뒤 상호작용 체크로 이동한다.
class SearchScreen extends ConsumerStatefulWidget {
  /// [SearchScreen] 생성자.
  const SearchScreen({super.key});

  @override
  ConsumerState<SearchScreen> createState() => _SearchScreenState();
}

class _SearchScreenState extends ConsumerState<SearchScreen> {
  final _searchController = TextEditingController();
  final _focusNode = FocusNode();

  @override
  void dispose() {
    _searchController.dispose();
    _focusNode.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final searchState = ref.watch(searchProvider);
    final notifier = ref.read(searchProvider.notifier);
    final hasSelection = searchState.selectedItems.isNotEmpty;
    final canCheck =
        searchState.selectedItems.length >= AppConstants.minInteractionItems;

    return Scaffold(
      appBar: AppBar(
        title: const Text('약/영양제 검색'),
      ),
      body: Column(
        children: [
          // 검색 입력 필드
          Padding(
            padding: const EdgeInsets.fromLTRB(16, 12, 16, 8),
            child: TextField(
              controller: _searchController,
              focusNode: _focusNode,
              onChanged: notifier.setQuery,
              decoration: InputDecoration(
                hintText: '약물 또는 영양제 이름을 검색하세요',
                hintStyle: const TextStyle(
                  color: AppColors.textDisabled,
                  fontSize: 14,
                ),
                prefixIcon: const Icon(
                  Icons.search,
                  color: AppColors.textSecondary,
                ),
                suffixIcon: searchState.query.isNotEmpty
                    ? IconButton(
                        icon: const Icon(
                          Icons.clear,
                          color: AppColors.textSecondary,
                        ),
                        onPressed: () {
                          _searchController.clear();
                          notifier.setQuery('');
                        },
                      )
                    : null,
                filled: true,
                fillColor: AppColors.background,
                contentPadding: const EdgeInsets.symmetric(
                  horizontal: 16,
                  vertical: 12,
                ),
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(12),
                  borderSide: BorderSide.none,
                ),
                enabledBorder: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(12),
                  borderSide:
                      const BorderSide(color: AppColors.divider, width: 0.5),
                ),
                focusedBorder: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(12),
                  borderSide:
                      const BorderSide(color: AppColors.primary, width: 1.5),
                ),
              ),
            ),
          ),

          // 필터 칩 행
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 16),
            child: Row(
              children: [
                _FilterChip(
                  label: '전체',
                  isSelected: searchState.filter == null,
                  onTap: () => notifier.setFilter(null),
                ),
                const SizedBox(width: 8),
                _FilterChip(
                  label: '약물',
                  isSelected: searchState.filter == ItemType.drug,
                  onTap: () => notifier.setFilter(ItemType.drug),
                ),
                const SizedBox(width: 8),
                _FilterChip(
                  label: '영양제',
                  isSelected: searchState.filter == ItemType.supplement,
                  onTap: () => notifier.setFilter(ItemType.supplement),
                ),
              ],
            ),
          ),

          const SizedBox(height: 8),

          // 검색 결과 리스트
          Expanded(
            child: searchState.query.isEmpty
                ? const EmptyStateWidget(
                    message: '약물이나 영양제를 검색하여\n상호작용을 확인해 보세요.',
                    icon: Icons.medication_outlined,
                  )
                : SearchResultList(
                    drugResults: searchState.drugResults,
                    supplementResults: searchState.supplementResults,
                    selectedItems: searchState.selectedItems,
                    onItemTap: notifier.toggleItem,
                    onRetry: notifier.search,
                  ),
          ),

          // 선택된 아이템 바
          if (hasSelection)
            SelectedItemsBar(
              selectedItems: searchState.selectedItems,
              onDelete: notifier.removeItem,
              onClear: notifier.clearSelection,
            ),

          // 상호작용 확인 버튼
          if (hasSelection)
            SafeArea(
              top: false,
              child: Padding(
                padding: const EdgeInsets.fromLTRB(16, 0, 16, 12),
                child: SizedBox(
                  width: double.infinity,
                  height: 52,
                  child: ElevatedButton(
                    onPressed: canCheck
                        ? () {
                            context.push(
                              '/result',
                              extra: searchState.selectedItems,
                            );
                          }
                        : null,
                    style: ElevatedButton.styleFrom(
                      backgroundColor: AppColors.primary,
                      foregroundColor: Colors.white,
                      disabledBackgroundColor: AppColors.divider,
                      disabledForegroundColor: AppColors.textDisabled,
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(12),
                      ),
                    ),
                    child: Text(
                      canCheck
                          ? '상호작용 확인 (${searchState.selectedItems.length}개)'
                          : '2개 이상 선택해 주세요',
                      style: const TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                  ),
                ),
              ),
            ),
        ],
      ),
    );
  }
}

/// 필터 칩 위젯.
class _FilterChip extends StatelessWidget {
  const _FilterChip({
    required this.label,
    required this.isSelected,
    required this.onTap,
  });

  final String label;
  final bool isSelected;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
        constraints: const BoxConstraints(minHeight: 48),
        decoration: BoxDecoration(
          color: isSelected ? AppColors.primary : AppColors.surface,
          borderRadius: BorderRadius.circular(20),
          border: Border.all(
            color: isSelected ? AppColors.primary : AppColors.divider,
          ),
        ),
        child: Center(
          child: Text(
            label,
            style: TextStyle(
              fontSize: 13,
              fontWeight: FontWeight.w500,
              color: isSelected ? Colors.white : AppColors.textSecondary,
            ),
          ),
        ),
      ),
    );
  }
}
