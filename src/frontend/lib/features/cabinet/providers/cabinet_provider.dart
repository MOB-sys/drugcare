import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'package:yakmeogeo/core/providers/service_providers.dart';
import 'package:yakmeogeo/features/cabinet/models/cabinet_item.dart';

/// 복약함 상태.
class CabinetState {
  /// 복약함 아이템 목록 (비동기 값).
  final AsyncValue<List<CabinetItem>> items;

  /// [CabinetState] 생성자.
  const CabinetState({
    this.items = const AsyncValue.loading(),
  });

  /// 상태를 복사하면서 일부 필드만 변경한다.
  CabinetState copyWith({AsyncValue<List<CabinetItem>>? items}) {
    return CabinetState(items: items ?? this.items);
  }
}

/// 복약함 상태 관리 노티파이어.
///
/// 아이템 조회, 추가, 삭제를 처리한다.
class CabinetNotifier extends StateNotifier<CabinetState> {
  /// [CabinetNotifier] 생성자.
  CabinetNotifier(this._ref) : super(const CabinetState()) {
    loadItems();
  }

  final Ref _ref;

  /// 복약함 아이템 목록을 서버에서 가져온다.
  Future<void> loadItems() async {
    state = state.copyWith(items: const AsyncValue.loading());
    try {
      final cabinetService = _ref.read(cabinetServiceProvider);
      final items = await cabinetService.listItems();
      state = state.copyWith(items: AsyncValue.data(items));
    } catch (e, st) {
      state = state.copyWith(items: AsyncValue.error(e, st));
    }
  }

  /// 복약함에 아이템을 추가하고 목록을 새로고침한다.
  ///
  /// [item] 추가할 아이템 생성 정보.
  Future<void> addItem(CabinetItemCreate item) async {
    try {
      final cabinetService = _ref.read(cabinetServiceProvider);
      await cabinetService.addItem(item);
      await loadItems();
    } catch (e, st) {
      state = state.copyWith(items: AsyncValue.error(e, st));
    }
  }

  /// 복약함에서 아이템을 삭제하고 목록을 새로고침한다.
  ///
  /// [itemId] 삭제할 아이템 ID.
  Future<void> deleteItem(int itemId) async {
    try {
      final cabinetService = _ref.read(cabinetServiceProvider);
      await cabinetService.deleteItem(itemId);
      await loadItems();
    } catch (e, st) {
      state = state.copyWith(items: AsyncValue.error(e, st));
    }
  }
}

/// 복약함 상태 프로바이더.
final cabinetProvider =
    StateNotifierProvider<CabinetNotifier, CabinetState>((ref) {
  return CabinetNotifier(ref);
});
