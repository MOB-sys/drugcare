import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import 'package:pillright/core/providers/service_providers.dart';
import 'package:pillright/core/theme/app_colors.dart';
import 'package:pillright/features/explore/data/explore_data.dart';
import 'package:pillright/features/explore/models/symptom_search_item.dart';
import 'package:pillright/features/explore/widgets/explore_result_card.dart';
import 'package:pillright/features/explore/widgets/keyword_chip_bar.dart';
import 'package:pillright/shared/models/paginated_result.dart';
import 'package:pillright/shared/widgets/common/empty_state_widget.dart';
import 'package:pillright/shared/widgets/common/loading_widget.dart';

/// 증상별 약물 검색 화면.
///
/// 사용자가 증상 키워드를 입력하거나 빠른 칩을 선택하여
/// 해당 증상에 효과가 있는 약물을 검색한다.
/// 복수 키워드를 선택하면 AND 조건으로 검색한다.
class SymptomSearchScreen extends ConsumerStatefulWidget {
  /// [SymptomSearchScreen] 생성자.
  const SymptomSearchScreen({super.key});

  @override
  ConsumerState<SymptomSearchScreen> createState() =>
      _SymptomSearchScreenState();
}

/// [SymptomSearchScreen]의 상태 관리 클래스.
class _SymptomSearchScreenState extends ConsumerState<SymptomSearchScreen> {
  /// 검색 입력 텍스트 컨트롤러.
  final _searchController = TextEditingController();

  /// 디바운스 타이머.
  Timer? _debounceTimer;

  /// 선택된 키워드 목록 (복수 AND 검색).
  final List<String> _selectedKeywords = [];

  /// 현재 페이지.
  int _currentPage = 1;

  /// 검색 결과.
  PaginatedResult<SymptomSearchItem>? _result;

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

  /// 칩 선택 시 키워드를 토글한다.
  void _onChipSelected(String keyword) {
    setState(() {
      if (_selectedKeywords.contains(keyword)) {
        _selectedKeywords.remove(keyword);
      } else {
        _selectedKeywords.add(keyword);
      }
      _currentPage = 1;
    });
    _searchController.clear();
    if (_selectedKeywords.isNotEmpty) {
      _performSearch();
    } else {
      setState(() {
        _result = null;
        _error = null;
      });
    }
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
        _result = null;
        _error = null;
      });
    }
  }

  /// 전체 초기화한다.
  void _clearAll() {
    _searchController.clear();
    setState(() {
      _selectedKeywords.clear();
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
      final result = await service.searchBySymptom(
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
      appBar: AppBar(title: const Text('증상별 약물 검색')),
      body: Column(
        children: [
          _buildSearchField(),
          const SizedBox(height: 8),
          KeywordChipBar(
            keywords: commonSymptoms,
            selectedKeywords: _selectedKeywords,
            onSelected: _onChipSelected,
          ),
          if (_selectedKeywords.isNotEmpty) _buildSelectedKeywordTags(),
          const SizedBox(height: 12),
          Expanded(child: _buildBody()),
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
          hintText: '증상을 입력하세요 (예: 두통, 소화불량)',
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
                  onPressed: _clearAll,
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

  /// 본문 영역을 상태에 따라 구성한다.
  Widget _buildBody() {
    if (_isLoading) {
      return const LoadingWidget(message: '증상별 약물을 검색 중...');
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

    if (_selectedKeywords.isEmpty) {
      return const EmptyStateWidget(
        message: '증상을 입력하면\n관련 약물을 찾아 드려요.',
        icon: Icons.healing_outlined,
      );
    }

    if (_result == null || _result!.items.isEmpty) {
      return const EmptyStateWidget(
        message: '검색 결과가 없습니다.\n다른 증상으로 검색해 보세요.',
        icon: Icons.search_off,
      );
    }

    return Column(
      children: [
        Expanded(
          child: ListView.builder(
            padding: const EdgeInsets.only(bottom: 8),
            itemCount: _result!.items.length,
            itemBuilder: (context, index) {
              final item = _result!.items[index];
              return ExploreResultCard(
                title: item.itemName,
                subtitle: item.entpName,
                snippet: item.efcyQesitm,
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
