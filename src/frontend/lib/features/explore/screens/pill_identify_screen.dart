import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import 'package:pillright/core/providers/service_providers.dart';
import 'package:pillright/core/theme/app_colors.dart';
import 'package:pillright/features/explore/data/pill_data.dart';
import 'package:pillright/features/explore/models/pill_identify_item.dart';
import 'package:pillright/shared/models/paginated_result.dart';
import 'package:pillright/shared/widgets/common/empty_state_widget.dart';
import 'package:pillright/shared/widgets/common/loading_widget.dart';

/// 알약 식별 화면.
///
/// 색상·모양·각인을 조합하여 알약을 텍스트 기반으로 식별한다.
class PillIdentifyScreen extends ConsumerStatefulWidget {
  /// [PillIdentifyScreen] 생성자.
  const PillIdentifyScreen({super.key});

  @override
  ConsumerState<PillIdentifyScreen> createState() =>
      _PillIdentifyScreenState();
}

/// [PillIdentifyScreen]의 상태 관리 클래스.
class _PillIdentifyScreenState extends ConsumerState<PillIdentifyScreen> {
  /// 각인 입력 텍스트 컨트롤러.
  final _imprintController = TextEditingController();

  /// 선택된 색상 값.
  String? _selectedColor;

  /// 선택된 모양 값.
  String? _selectedShape;

  /// 현재 페이지.
  int _currentPage = 1;

  /// 검색 결과.
  PaginatedResult<PillIdentifyItem>? _result;

  /// 로딩 상태.
  bool _isLoading = false;

  /// 에러 메시지.
  String? _error;

  /// 검색 수행 여부.
  bool _hasSearched = false;

  /// 검색 조건이 하나라도 선택되었는지 확인한다.
  bool get _hasAnyCriteria =>
      _selectedColor != null ||
      _selectedShape != null ||
      _imprintController.text.trim().isNotEmpty;

  @override
  void dispose() {
    _imprintController.dispose();
    super.dispose();
  }

  /// 알약 식별 검색을 수행한다.
  Future<void> _performSearch() async {
    if (!_hasAnyCriteria) return;

    setState(() {
      _isLoading = true;
      _error = null;
      _hasSearched = true;
    });

    try {
      final service = ref.read(drugServiceProvider);
      final result = await service.identifyPill(
        color: _selectedColor,
        shape: _selectedShape,
        imprint: _imprintController.text.trim(),
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

  /// 색상을 선택/해제한다.
  void _onColorSelected(String value) {
    setState(() {
      _selectedColor = _selectedColor == value ? null : value;
    });
  }

  /// 모양을 선택/해제한다.
  void _onShapeSelected(String value) {
    setState(() {
      _selectedShape = _selectedShape == value ? null : value;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('알약 식별')),
      body: Column(
        children: [
          Expanded(
            child: ListView(
              padding: const EdgeInsets.fromLTRB(16, 12, 16, 0),
              children: [
                _buildSectionTitle('색상 선택'),
                const SizedBox(height: 8),
                _buildColorGrid(),
                const SizedBox(height: 20),
                _buildSectionTitle('모양 선택'),
                const SizedBox(height: 8),
                _buildShapeGrid(),
                const SizedBox(height: 20),
                _buildSectionTitle('각인 입력'),
                const SizedBox(height: 8),
                _buildImprintField(),
                const SizedBox(height: 20),
                _buildSearchButton(),
                const SizedBox(height: 20),
                _buildResultArea(),
              ],
            ),
          ),
        ],
      ),
    );
  }

  /// 섹션 제목을 구성한다.
  Widget _buildSectionTitle(String title) {
    return Text(
      title,
      style: Theme.of(context).textTheme.titleSmall?.copyWith(
            fontWeight: FontWeight.w700,
          ),
    );
  }

  /// 색상 그리드를 구성한다.
  Widget _buildColorGrid() {
    return Wrap(
      spacing: 10,
      runSpacing: 10,
      children: pillColors.map((color) {
        final isSelected = _selectedColor == color.value;
        final isWhite = color.colorCode == 0xFFFFFFFF;
        final isTransparent = color.colorCode == 0x00000000;

        return GestureDetector(
          onTap: () => _onColorSelected(color.value),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Container(
                width: 40,
                height: 40,
                decoration: BoxDecoration(
                  color: isTransparent
                      ? null
                      : Color(color.colorCode),
                  shape: BoxShape.circle,
                  border: Border.all(
                    color: isSelected
                        ? AppColors.primary
                        : isWhite || isTransparent
                            ? AppColors.divider
                            : Colors.transparent,
                    width: isSelected ? 2.5 : 1,
                  ),
                  gradient: isTransparent
                      ? const LinearGradient(
                          colors: [
                            Color(0xFFE0E0E0),
                            Color(0xFFFFFFFF),
                            Color(0xFFE0E0E0),
                            Color(0xFFFFFFFF),
                          ],
                          stops: [0.0, 0.25, 0.5, 0.75],
                          begin: Alignment.topLeft,
                          end: Alignment.bottomRight,
                        )
                      : null,
                ),
                child: isSelected
                    ? Icon(
                        Icons.check,
                        size: 20,
                        color: isWhite || isTransparent
                            ? AppColors.primary
                            : Colors.white,
                      )
                    : null,
              ),
              const SizedBox(height: 4),
              Text(
                color.label,
                style: TextStyle(
                  fontSize: 11,
                  color: isSelected
                      ? AppColors.primary
                      : AppColors.textSecondary,
                  fontWeight:
                      isSelected ? FontWeight.w600 : FontWeight.normal,
                ),
              ),
            ],
          ),
        );
      }).toList(),
    );
  }

  /// 모양 그리드를 구성한다.
  Widget _buildShapeGrid() {
    return Wrap(
      spacing: 8,
      runSpacing: 8,
      children: pillShapes.map((shape) {
        final isSelected = _selectedShape == shape.value;

        return ChoiceChip(
          label: Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              Text(
                shape.icon,
                style: const TextStyle(fontSize: 14),
              ),
              const SizedBox(width: 4),
              Text(shape.label),
            ],
          ),
          selected: isSelected,
          onSelected: (_) => _onShapeSelected(shape.value),
          selectedColor: AppColors.primary.withValues(alpha: 0.15),
          labelStyle: TextStyle(
            color: isSelected ? AppColors.primary : AppColors.textPrimary,
            fontWeight: isSelected ? FontWeight.w600 : FontWeight.normal,
            fontSize: 13,
          ),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(8),
            side: BorderSide(
              color: isSelected ? AppColors.primary : AppColors.divider,
            ),
          ),
          showCheckmark: false,
        );
      }).toList(),
    );
  }

  /// 각인 입력 필드를 구성한다.
  Widget _buildImprintField() {
    final borderRadius = BorderRadius.circular(12);

    return TextField(
      controller: _imprintController,
      decoration: InputDecoration(
        hintText: '알약에 새겨진 문자를 입력하세요',
        hintStyle: const TextStyle(
          color: AppColors.textDisabled,
          fontSize: 14,
        ),
        prefixIcon: const Icon(
          Icons.text_fields,
          color: AppColors.textSecondary,
        ),
        suffixIcon: _imprintController.text.isNotEmpty
            ? IconButton(
                icon: const Icon(
                  Icons.clear,
                  color: AppColors.textSecondary,
                ),
                onPressed: () {
                  _imprintController.clear();
                  setState(() {});
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
      onChanged: (_) => setState(() {}),
    );
  }

  /// 검색 버튼을 구성한다.
  Widget _buildSearchButton() {
    return SizedBox(
      width: double.infinity,
      child: FilledButton.icon(
        onPressed: _hasAnyCriteria
            ? () {
                _currentPage = 1;
                _performSearch();
              }
            : null,
        icon: const Icon(Icons.search, size: 20),
        label: const Text(
          '알약 찾기',
          style: TextStyle(fontSize: 15, fontWeight: FontWeight.w600),
        ),
        style: FilledButton.styleFrom(
          backgroundColor: AppColors.primary,
          disabledBackgroundColor: AppColors.divider,
          padding: const EdgeInsets.symmetric(vertical: 14),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
          ),
        ),
      ),
    );
  }

  /// 결과 영역을 상태에 따라 구성한다.
  Widget _buildResultArea() {
    if (_isLoading) {
      return const Padding(
        padding: EdgeInsets.only(top: 40),
        child: LoadingWidget(message: '알약을 검색 중...'),
      );
    }

    if (_error != null) {
      return Padding(
        padding: const EdgeInsets.only(top: 40),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Icon(
              Icons.error_outline,
              size: 48,
              color: AppColors.textDisabled,
            ),
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

    if (!_hasSearched) {
      return const Padding(
        padding: EdgeInsets.only(top: 40),
        child: EmptyStateWidget(
          message: '색상·모양·각인을 선택하고\n알약 찾기를 눌러주세요.',
          icon: Icons.medication_outlined,
        ),
      );
    }

    if (_result == null || _result!.items.isEmpty) {
      return const Padding(
        padding: EdgeInsets.only(top: 40),
        child: EmptyStateWidget(
          message: '일치하는 알약이 없습니다.\n조건을 변경해 보세요.',
          icon: Icons.search_off,
        ),
      );
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          '검색 결과 ${_result!.total}건',
          style: const TextStyle(
            fontSize: 13,
            color: AppColors.textSecondary,
            fontWeight: FontWeight.w500,
          ),
        ),
        const SizedBox(height: 8),
        ...List.generate(_result!.items.length, (index) {
          final item = _result!.items[index];
          return _buildResultCard(item);
        }),
        if (_result!.totalPages > 1) _buildPagination(),
        const SizedBox(height: 16),
      ],
    );
  }

  /// 결과 카드를 구성한다.
  Widget _buildResultCard(PillIdentifyItem item) {
    return Card(
      margin: const EdgeInsets.only(bottom: 8),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
      ),
      elevation: 0,
      color: AppColors.surface,
      child: InkWell(
        onTap: () => context.push('/drugs/${item.id}'),
        borderRadius: BorderRadius.circular(12),
        child: Padding(
          padding: const EdgeInsets.all(12),
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              _buildDrugImage(item.itemImage),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      item.itemName,
                      style: const TextStyle(
                        fontSize: 15,
                        fontWeight: FontWeight.w600,
                        color: AppColors.textPrimary,
                      ),
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                    ),
                    if (item.entpName != null) ...[
                      const SizedBox(height: 2),
                      Text(
                        item.entpName!,
                        style: const TextStyle(
                          fontSize: 12,
                          color: AppColors.textSecondary,
                        ),
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                      ),
                    ],
                    if (item.chart != null &&
                        item.chart!.isNotEmpty) ...[
                      const SizedBox(height: 6),
                      Text(
                        item.chart!,
                        style: const TextStyle(
                          fontSize: 12,
                          color: AppColors.textSecondary,
                          height: 1.4,
                        ),
                        maxLines: 2,
                        overflow: TextOverflow.ellipsis,
                      ),
                    ],
                  ],
                ),
              ),
              const SizedBox(width: 4),
              const Icon(
                Icons.chevron_right,
                color: AppColors.textDisabled,
                size: 20,
              ),
            ],
          ),
        ),
      ),
    );
  }

  /// 약물 이미지를 구성한다.
  Widget _buildDrugImage(String? imageUrl) {
    if (imageUrl != null && imageUrl.isNotEmpty) {
      return ClipRRect(
        borderRadius: BorderRadius.circular(8),
        child: Image.network(
          imageUrl,
          width: 56,
          height: 56,
          fit: BoxFit.cover,
          errorBuilder: (_, __, ___) => _buildImagePlaceholder(),
        ),
      );
    }
    return _buildImagePlaceholder();
  }

  /// 이미지 플레이스홀더를 구성한다.
  Widget _buildImagePlaceholder() {
    return Container(
      width: 56,
      height: 56,
      decoration: BoxDecoration(
        color: AppColors.primaryLight,
        borderRadius: BorderRadius.circular(8),
      ),
      child: const Icon(
        Icons.medication_outlined,
        color: AppColors.primary,
        size: 24,
      ),
    );
  }

  /// 페이지네이션 컨트롤을 구성한다.
  Widget _buildPagination() {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          TextButton(
            onPressed: _currentPage > 1
                ? () => _goToPage(_currentPage - 1)
                : null,
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
    );
  }
}
