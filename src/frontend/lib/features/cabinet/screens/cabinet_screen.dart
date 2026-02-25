import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import 'package:yakmeogeo/core/constants/app_constants.dart';
import 'package:yakmeogeo/core/theme/app_colors.dart';
import 'package:yakmeogeo/features/cabinet/models/cabinet_item.dart';
import 'package:yakmeogeo/features/cabinet/providers/cabinet_provider.dart';
import 'package:yakmeogeo/features/cabinet/widgets/cabinet_item_tile.dart';
import 'package:yakmeogeo/features/search/models/selected_search_item.dart';
import 'package:yakmeogeo/shared/widgets/common/empty_state_widget.dart';
import 'package:yakmeogeo/shared/widgets/common/error_widget.dart';
import 'package:yakmeogeo/shared/widgets/common/loading_widget.dart';

/// 복약함 관리 화면.
///
/// 등록된 약물/영양제를 관리하고, 전체 상호작용을 확인할 수 있다.
class CabinetScreen extends ConsumerWidget {
  /// [CabinetScreen] 생성자.
  const CabinetScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final cabinetState = ref.watch(cabinetProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('내 복약함'),
        centerTitle: false,
      ),
      body: cabinetState.items.when(
        data: (items) => _buildItemList(context, ref, items),
        loading: () => const LoadingWidget(message: '복약함을 불러오는 중...'),
        error: (error, _) => AppErrorWidget(
          message: '복약함을 불러올 수 없습니다.\n$error',
          onRetry: () => ref.read(cabinetProvider.notifier).loadItems(),
        ),
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: () => context.push('/search?mode=cabinet'),
        backgroundColor: AppColors.primary,
        child: const Icon(Icons.add, color: Colors.white),
      ),
    );
  }

  /// 복약함 아이템 목록을 빌드한다.
  Widget _buildItemList(
    BuildContext context,
    WidgetRef ref,
    List<CabinetItem> items,
  ) {
    if (items.isEmpty) {
      return const EmptyStateWidget(
        message: '복약함이 비어있습니다.\n+ 버튼을 눌러 약물이나 영양제를 추가하세요.',
        icon: Icons.medical_services_outlined,
      );
    }

    return Column(
      children: [
        Expanded(
          child: ListView.builder(
            padding: const EdgeInsets.fromLTRB(16, 16, 16, 80),
            itemCount: items.length,
            itemBuilder: (context, index) =>
                _buildListItem(context, ref, items[index]),
          ),
        ),
        if (items.length >= AppConstants.minInteractionItems)
          _buildCheckButton(context, items),
      ],
    );
  }

  /// 복약함의 개별 아이템 위젯을 빌드한다.
  ///
  /// 스와이프 삭제(Dismissible)와 [CabinetItemTile]을 포함한다.
  Widget _buildListItem(
    BuildContext context,
    WidgetRef ref,
    CabinetItem item,
  ) {
    return Dismissible(
      key: ValueKey(item.id),
      direction: DismissDirection.endToStart,
      background: Container(
        alignment: Alignment.centerRight,
        padding: const EdgeInsets.only(right: 20),
        margin: const EdgeInsets.only(bottom: 8),
        decoration: BoxDecoration(
          color: AppColors.danger,
          borderRadius: BorderRadius.circular(10),
        ),
        child: const Icon(Icons.delete, color: Colors.white),
      ),
      confirmDismiss: (_) => _confirmDelete(context, item),
      onDismissed: (_) {
        ref.read(cabinetProvider.notifier).deleteItem(item.id);
      },
      child: Padding(
        padding: const EdgeInsets.only(bottom: 8),
        child: CabinetItemTile(
          item: item,
          onDelete: () => _handleDelete(context, ref, item),
        ),
      ),
    );
  }

  /// 전체 상호작용 확인 버튼 영역을 빌드한다.
  ///
  /// [SafeArea]로 감싸 하단 영역에 안전하게 배치된다.
  Widget _buildCheckButton(
    BuildContext context,
    List<CabinetItem> items,
  ) {
    return SafeArea(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: SizedBox(
          width: double.infinity,
          height: 48,
          child: ElevatedButton(
            onPressed: () => _checkAllInteractions(context, items),
            style: ElevatedButton.styleFrom(
              backgroundColor: AppColors.primary,
              foregroundColor: Colors.white,
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(12),
              ),
            ),
            child: const Text(
              '전체 상호작용 확인',
              style: TextStyle(fontSize: 16, fontWeight: FontWeight.w600),
            ),
          ),
        ),
      ),
    );
  }

  /// 삭제 확인 다이얼로그를 표시한다.
  Future<bool?> _confirmDelete(BuildContext context, CabinetItem item) {
    return showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('삭제 확인'),
        content: Text("'${item.itemName}'을(를) 복약함에서 삭제하시겠습니까?"),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(false),
            child: const Text('취소'),
          ),
          TextButton(
            onPressed: () => Navigator.of(context).pop(true),
            style: TextButton.styleFrom(foregroundColor: AppColors.danger),
            child: const Text('삭제'),
          ),
        ],
      ),
    );
  }

  /// 삭제 버튼 처리 (확인 후 삭제).
  Future<void> _handleDelete(
    BuildContext context,
    WidgetRef ref,
    CabinetItem item,
  ) async {
    final confirmed = await _confirmDelete(context, item);
    if (confirmed == true) {
      ref.read(cabinetProvider.notifier).deleteItem(item.id);
    }
  }

  /// 전체 복약함 아이템의 상호작용을 확인한다.
  void _checkAllInteractions(BuildContext context, List<CabinetItem> items) {
    final selectedItems = items
        .map(
          (item) => SelectedSearchItem(
            itemType: item.itemType,
            itemId: item.itemId,
            name: item.itemName,
          ),
        )
        .toList();

    context.push('/result', extra: selectedItems);
  }
}
