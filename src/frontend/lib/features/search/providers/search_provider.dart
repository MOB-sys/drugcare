import 'dart:async';

import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'package:pillright/core/constants/app_constants.dart';
import 'package:pillright/core/providers/service_providers.dart';
import 'package:pillright/features/search/models/drug_search_item.dart';
import 'package:pillright/features/search/models/selected_search_item.dart';
import 'package:pillright/features/search/models/supplement_search_item.dart';
import 'package:pillright/shared/models/item_type.dart';
import 'package:pillright/shared/models/paginated_result.dart';

/// 검색 화면 상태.
class SearchState {
  /// 검색어.
  final String query;

  /// 필터 (null=전체, drug=약물만, supplement=영양제만).
  final ItemType? filter;

  /// 약물 검색 결과.
  final AsyncValue<PaginatedResult<DrugSearchItem>?> drugResults;

  /// 영양제 검색 결과.
  final AsyncValue<PaginatedResult<SupplementSearchItem>?> supplementResults;

  /// 선택된 아이템 목록.
  final List<SelectedSearchItem> selectedItems;

  /// 현재 페이지.
  final int currentPage;

  /// [SearchState] 생성자.
  const SearchState({
    this.query = '',
    this.filter,
    this.drugResults = const AsyncValue.data(null),
    this.supplementResults = const AsyncValue.data(null),
    this.selectedItems = const [],
    this.currentPage = 1,
  });

  /// 상태 복사본을 생성한다.
  SearchState copyWith({
    String? query,
    ItemType? Function()? filter,
    AsyncValue<PaginatedResult<DrugSearchItem>?>? drugResults,
    AsyncValue<PaginatedResult<SupplementSearchItem>?>? supplementResults,
    List<SelectedSearchItem>? selectedItems,
    int? currentPage,
  }) {
    return SearchState(
      query: query ?? this.query,
      filter: filter != null ? filter() : this.filter,
      drugResults: drugResults ?? this.drugResults,
      supplementResults: supplementResults ?? this.supplementResults,
      selectedItems: selectedItems ?? this.selectedItems,
      currentPage: currentPage ?? this.currentPage,
    );
  }
}

/// 검색 화면 상태 관리 노티파이어.
class SearchNotifier extends StateNotifier<SearchState> {
  /// [SearchNotifier] 생성자.
  SearchNotifier(this._ref) : super(const SearchState());

  /// Riverpod Ref 참조.
  final Ref _ref;

  /// 검색어 디바운스 타이머.
  Timer? _debounceTimer;

  /// 검색어를 설정하고 디바운스 검색을 트리거한다.
  void setQuery(String query) {
    state = state.copyWith(query: query, currentPage: 1);
    _debounceTimer?.cancel();

    if (query.isEmpty) {
      state = state.copyWith(
        drugResults: const AsyncValue.data(null),
        supplementResults: const AsyncValue.data(null),
      );
      return;
    }

    _debounceTimer = Timer(
      const Duration(milliseconds: AppConstants.searchDebounceMs),
      search,
    );
  }

  /// 필터를 변경한다 (null=전체, drug=약물만, supplement=영양제만).
  void setFilter(ItemType? filter) {
    state = state.copyWith(filter: () => filter, currentPage: 1);
    if (state.query.isNotEmpty) {
      search();
    }
  }

  /// 현재 검색어와 필터로 검색을 실행한다.
  Future<void> search() async {
    final query = state.query;
    if (query.isEmpty) return;

    final filter = state.filter;
    final page = state.currentPage;
    const pageSize = AppConstants.defaultPageSize;

    final searchDrug = filter == null || filter == ItemType.drug;
    final searchSupplement = filter == null || filter == ItemType.supplement;

    // 로딩 상태 설정
    if (searchDrug) {
      state = state.copyWith(drugResults: const AsyncValue.loading());
    } else {
      state = state.copyWith(drugResults: const AsyncValue.data(null));
    }
    if (searchSupplement) {
      state = state.copyWith(supplementResults: const AsyncValue.loading());
    } else {
      state = state.copyWith(supplementResults: const AsyncValue.data(null));
    }

    // 병렬 검색 실행
    final futures = <Future<void>>[];

    if (searchDrug) {
      futures.add(_searchDrugs(query, page, pageSize));
    }
    if (searchSupplement) {
      futures.add(_searchSupplements(query, page, pageSize));
    }

    await Future.wait(futures);
  }

  Future<void> _searchDrugs(String query, int page, int pageSize) async {
    try {
      final drugService = _ref.read(drugServiceProvider);
      final result = await drugService.searchDrugs(
        query,
        page: page,
        pageSize: pageSize,
      );
      if (mounted) {
        state = state.copyWith(drugResults: AsyncValue.data(result));
      }
    } catch (e, st) {
      if (mounted) {
        state = state.copyWith(drugResults: AsyncValue.error(e, st));
      }
    }
  }

  Future<void> _searchSupplements(String query, int page, int pageSize) async {
    try {
      final supplementService = _ref.read(supplementServiceProvider);
      final result = await supplementService.searchSupplements(
        query,
        page: page,
        pageSize: pageSize,
      );
      if (mounted) {
        state = state.copyWith(supplementResults: AsyncValue.data(result));
      }
    } catch (e, st) {
      if (mounted) {
        state = state.copyWith(supplementResults: AsyncValue.error(e, st));
      }
    }
  }

  /// 아이템 선택을 토글한다 (추가/제거).
  ///
  /// 최대 [AppConstants.maxInteractionItems]개까지 선택 가능.
  void toggleItem(SelectedSearchItem item) {
    final current = List<SelectedSearchItem>.from(state.selectedItems);
    final index = current.indexWhere(
      (e) => e.itemType == item.itemType && e.itemId == item.itemId,
    );

    if (index >= 0) {
      current.removeAt(index);
    } else {
      if (current.length >= AppConstants.maxInteractionItems) return;
      current.add(item);
    }

    state = state.copyWith(selectedItems: current);
  }

  /// 선택 목록에서 아이템을 제거한다.
  void removeItem(SelectedSearchItem item) {
    final current = List<SelectedSearchItem>.from(state.selectedItems);
    current.removeWhere(
      (e) => e.itemType == item.itemType && e.itemId == item.itemId,
    );
    state = state.copyWith(selectedItems: current);
  }

  /// 모든 선택을 해제한다.
  void clearSelection() {
    state = state.copyWith(selectedItems: []);
  }

  /// 다음 페이지 결과를 로드한다.
  void loadMore() {
    state = state.copyWith(currentPage: state.currentPage + 1);
    search();
  }

  @override
  void dispose() {
    _debounceTimer?.cancel();
    super.dispose();
  }
}

/// 검색 상태 프로바이더.
final searchProvider =
    StateNotifierProvider.autoDispose<SearchNotifier, SearchState>((ref) {
  return SearchNotifier(ref);
});
