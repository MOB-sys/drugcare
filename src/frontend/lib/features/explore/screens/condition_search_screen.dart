import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import 'package:pillright/core/providers/service_providers.dart';
import 'package:pillright/core/theme/app_colors.dart';
import 'package:pillright/features/explore/data/explore_data.dart';
import 'package:pillright/features/explore/models/condition_search_item.dart';
import 'package:pillright/features/explore/widgets/explore_result_card.dart';
import 'package:pillright/shared/models/paginated_result.dart';
import 'package:pillright/shared/widgets/common/empty_state_widget.dart';
import 'package:pillright/shared/widgets/common/loading_widget.dart';

/// 질환별 주의 약물 화면.
///
/// 초기에는 질환 카테고리 카드 그리드를 표시하고,
/// 카테고리 선택 또는 직접 검색 시 해당 질환의 주의 약물 목록을 보여준다.
/// 복수 키워드를 선택하면 AND 조건으로 검색한다.
class ConditionSearchScreen extends ConsumerStatefulWidget {
  /// [ConditionSearchScreen] 생성자.
  const ConditionSearchScreen({super.key});

  @override
  ConsumerState<ConditionSearchScreen> createState() =>
      _ConditionSearchScreenState();
}

/// [ConditionSearchScreen]의 상태 관리 클래스.
class _ConditionSearchScreenState
    extends ConsumerState<ConditionSearchScreen> {
  /// 검색 입력 텍스트 컨트롤러.
  final _searchController = TextEditingController();

  /// 디바운스 타이머.
  Timer? _debounceTimer;

  /// 선택된 키워드 목록 (복수 AND 검색).
  final List<String> _selectedKeywords = [];

  /// 카드 그리드 모드 여부.
  bool _showGrid = true;

  /// 현재 페이지.
  int _currentPage = 1;

  /// 검색 결과.
  PaginatedResult<ConditionSearchItem>? _result;

  /// 로딩 상태.
  bool _isLoading = false;

  /// 에러 메시지.
  String? _error;

  /// 현재 검색어 (선택된 키워드를 공백으로 합친 값).
  String get _query => _selectedKeywords.join(' ');

  @override
  void dispose() {
    _searchController.dispose();
    _debounceTimer?.cancel();
    super.dispose();
  }

  /// 검색어 입력 후 제출 시 키워드를 추가한다.
  void _onSearchSubmitted(String value) {
    final newKeywords = value
        .trim()
        .split(RegExp(r'\s+'))
        .where((k) => k.isNotEmpty)
        .toList();
    if (newKeywords.isEmpty) return;

    setState(() {
      for (final keyword in newKeywords) {
        if (!_selectedKeywords.contains(keyword)) {
          _selectedKeywords.add(keyword);
        }
      }
      _showGrid = false;
      _currentPage = 1;
    });
    _searchController.clear();
    _performSearch();
  }

  /// 검색어 변경 시 디바운스 처리한다.
  void _onQueryChanged(String value) {
    _debounceTimer?.cancel();
    _debounceTimer = Timer(const Duration(milliseconds: 500), () {
      if (value.trim().isNotEmpty) {
        _onSearchSubmitted(value);
      }
    });
  }

  /// 카테고리 카드를 선택한다.
  void _onCategorySelected(ConditionCategory category) {
    setState(() {
      if (!_selectedKeywords.contains(category.keyword)) {
        _selectedKeywords.add(category.keyword);
      }
      _showGrid = false;
      _currentPage = 1;
    });
    _searchController.clear();
    _performSearch();
  }

  /// 개별 키워드를 제거한다.
  void _removeKeyword(String keyword) {
    setState(() {
      _selectedKeywords.remove(keyword);
      _currentPage = 1;
    });
    if (_selectedKeywords.isNotEmpty) {
      _performSearch();
    } else {
      setState(() {
        _showGrid = true;
        _result = null;
        _error = null;
      });
    }
  }

  /// 카드 그리드로 돌아간다.
  void _backToGrid() {
    _searchController.clear();
    setState(() {
      _selectedKeywords.clear();
      _showGrid = true;
      _result = null;
      _error = null;
    });
  }

  /// API 호출을 수행한다.
  Future<void> _performSearch() async {
    if (_query.isEmpty) return;

    setState(() {
      _isLoading = true;
      _error = null;
    });

    try {
      final service = ref.read(drugServiceProvider);
      final result = await service.searchByCondition(
        _query,
        page: _currentPage,
      );
      if (mounted) {
        setState(() {
          _result = result;
          _isLoading = false;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _error = '검색 중 오류가 발생했습니다.';
          _isLoading = false;
        });
      }
    }
  }

  /// 페이지를 변경한다.
  void _goToPage(int page) {
    setState(() => _currentPage = page);
    _performSearch();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('질환별 주의 약물')),
      body: Column(
        children: [
          _buildSearchField(),
          if (!_showGrid && _selectedKeywords.isNotEmpty)
            _buildSelectedKeywordTags(),
          const SizedBox(height: 12),
          Expanded(child: _showGrid ? _buildCategoryGrid() : _buildBody()),
        ],
      ),
    );
  }

  /// 검색 입력 필드를 구성한다.
  Widget _buildSearchField() {
    final borderRadius = BorderRadius.circular(12);

    return Padding(
      padding: const EdgeInsets.fromLTRB(16, 12, 16, 0),
      child: TextField(
        controller: _searchController,
        onChanged: _onQueryChanged,
        onSubmitted: _onSearchSubmitted,
        textInputAction: TextInputAction.search,
        decoration: InputDecoration(
          hintText: '질환명을 입력하세요 (예: 고혈압, 당뇨)',
          hintStyle: const TextStyle(
            color: AppColors.textDisabled,
            fontSize: 14,
          ),
          prefixIcon:
              const Icon(Icons.search, color: AppColors.textSecondary),
          suffixIcon: _selectedKeywords.isNotEmpty
              ? IconButton(
                  icon: const Icon(Icons.clear,
                      color: AppColors.textSecondary),
                  onPressed: _backToGrid,
                )
              : null,
          filled: true,
          fillColor: AppColors.background,
          contentPadding: const EdgeInsets.symmetric(
            horizontal: 16,
            vertical: 12,
          ),
          border: OutlineInputBorder(
            borderRadius: borderRadius,
            borderSide: BorderSide.none,
          ),
          enabledBorder: OutlineInputBorder(
            borderRadius: borderRadius,
            borderSide:
                const BorderSide(color: AppColors.divider, width: 0.5),
          ),
          focusedBorder: OutlineInputBorder(
            borderRadius: borderRadius,
            borderSide:
                const BorderSide(color: AppColors.primary, width: 1.5),
          ),
        ),
      ),
    );
  }

  /// 선택된 키워드 태그 목록을 구성한다.
  Widget _buildSelectedKeywordTags() {
    return Padding(
      padding: const EdgeInsets.fromLTRB(16, 8, 16, 0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            '${_selectedKeywords.length}개 키워드로 검색',
            style: const TextStyle(
              fontSize: 12,
              color: AppColors.textSecondary,
            ),
          ),
          const SizedBox(height: 4),
          Wrap(
            spacing: 6,
            runSpacing: 4,
            children: _selectedKeywords.map((keyword) {
              return Chip(
                label: Text(
                  keyword,
                  style: const TextStyle(fontSize: 12, color: Colors.white),
                ),
                deleteIcon: const Icon(Icons.close, size: 16),
                deleteIconColor: Colors.white70,
                onDeleted: () => _removeKeyword(keyword),
                backgroundColor: AppColors.primary,
                side: BorderSide.none,
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(16),
                ),
                materialTapTargetSize: MaterialTapTargetSize.shrinkWrap,
                visualDensity: VisualDensity.compact,
              );
            }).toList(),
          ),
        ],
      ),
    );
  }

  /// 질환 카테고리 카드 그리드를 구성한다.
  Widget _buildCategoryGrid() {
    return GridView.builder(
      padding: const EdgeInsets.all(16),
      gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
        crossAxisCount: 2,
        mainAxisSpacing: 12,
        crossAxisSpacing: 12,
        childAspectRatio: 1.6,
      ),
      itemCount: conditionCategories.length,
      itemBuilder: (context, index) {
        final category = conditionCategories[index];
        return _buildCategoryCard(category);
      },
    );
  }

  /// 개별 카테고리 카드를 구성한다.
  Widget _buildCategoryCard(ConditionCategory category) {
    return Card(
      elevation: 0,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
        side: const BorderSide(color: AppColors.divider, width: 0.5),
      ),
      color: AppColors.surface,
      child: InkWell(
        onTap: () => _onCategorySelected(category),
        borderRadius: BorderRadius.circular(12),
        child: Padding(
          padding: const EdgeInsets.all(12),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Text(
                category.label,
                style: const TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.w600,
                  color: AppColors.textPrimary,
                ),
              ),
              const SizedBox(height: 4),
              Text(
                category.description,
                style: const TextStyle(
                  fontSize: 12,
                  color: AppColors.textSecondary,
                ),
                maxLines: 2,
                overflow: TextOverflow.ellipsis,
              ),
            ],
          ),
        ),
      ),
    );
  }

  /// 검색 결과 본문을 구성한다.
  Widget _buildBody() {
    if (_isLoading) {
      return const LoadingWidget(message: '질환별 주의 약물을 검색 중...');
    }

    if (_error != null) {
      return Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Icon(Icons.error_outline,
                size: 48, color: AppColors.textDisabled),
            const SizedBox(height: 12),
            Text(
              _error!,
              style: const TextStyle(color: AppColors.textSecondary),
            ),
            const SizedBox(height: 12),
            TextButton(
              onPressed: _performSearch,
              child: const Text('다시 시도'),
            ),
          ],
        ),
      );
    }

    if (_result == null || _result!.items.isEmpty) {
      return Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const EmptyStateWidget(
            message: '검색 결과가 없습니다.\n다른 질환으로 검색해 보세요.',
            icon: Icons.search_off,
          ),
          const SizedBox(height: 16),
          TextButton.icon(
            onPressed: _backToGrid,
            icon: const Icon(Icons.grid_view, size: 18),
            label: const Text('질환 목록으로'),
          ),
        ],
      );
    }

    return Column(
      children: [
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 16),
          child: Row(
            children: [
              Expanded(
                child: Text(
                  '${_selectedKeywords.join(', ')} 관련 주의 약물',
                  style: const TextStyle(
                    fontSize: 14,
                    fontWeight: FontWeight.w600,
                    color: AppColors.textPrimary,
                  ),
                  overflow: TextOverflow.ellipsis,
                ),
              ),
              TextButton.icon(
                onPressed: _backToGrid,
                icon: const Icon(Icons.grid_view, size: 16),
                label: const Text('질환 목록으로'),
                style: TextButton.styleFrom(
                  foregroundColor: AppColors.textSecondary,
                  textStyle: const TextStyle(fontSize: 12),
                ),
              ),
            ],
          ),
        ),
        Expanded(
          child: ListView.builder(
            padding: const EdgeInsets.only(bottom: 8),
            itemCount: _result!.items.length,
            itemBuilder: (context, index) {
              final item = _result!.items[index];
              final snippet =
                  item.atpnWarnQesitm ?? item.atpnQesitm ?? '';
              return ExploreResultCard(
                title: item.itemName,
                subtitle: item.entpName,
                snippet: snippet,
                highlightKeyword: _query,
                imageUrl: item.itemImage,
                onTap: () {
                  context.push('/drugs/${item.id}');
                },
              );
            },
          ),
        ),
        if (_result!.totalPages > 1) _buildPagination(),
      ],
    );
  }

  /// 페이지네이션 컨트롤을 구성한다.
  Widget _buildPagination() {
    return SafeArea(
      top: false,
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            TextButton(
              onPressed:
                  _currentPage > 1 ? () => _goToPage(_currentPage - 1) : null,
              child: const Text('이전'),
            ),
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16),
              child: Text(
                '$_currentPage / ${_result!.totalPages}',
                style: const TextStyle(
                  fontSize: 14,
                  color: AppColors.textSecondary,
                ),
              ),
            ),
            TextButton(
              onPressed: _currentPage < _result!.totalPages
                  ? () => _goToPage(_currentPage + 1)
                  : null,
              child: const Text('다음'),
            ),
          ],
        ),
      ),
    );
  }
}
