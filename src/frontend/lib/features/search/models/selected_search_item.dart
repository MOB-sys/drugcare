import 'package:pillright/shared/models/item_type.dart';

/// 검색에서 선택된 아이템 (상호작용 체크로 전달용 경량 모델).
class SelectedSearchItem {
  /// 아이템 유형 (약물/영양제).
  final ItemType itemType;

  /// 아이템 ID.
  final int itemId;

  /// 아이템 이름.
  final String name;

  /// [SelectedSearchItem] 생성자.
  const SelectedSearchItem({
    required this.itemType,
    required this.itemId,
    required this.name,
  });
}
