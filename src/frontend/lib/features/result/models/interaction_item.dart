import 'package:yakmeogeo/shared/models/item_type.dart';

/// 상호작용 체크 요청용 아이템.
class InteractionItem {
  /// 아이템 유형 (약물/영양제).
  final ItemType itemType;

  /// 아이템 ID.
  final int itemId;

  /// [InteractionItem] 생성자.
  const InteractionItem({
    required this.itemType,
    required this.itemId,
  });

  /// JSON으로 변환한다.
  Map<String, dynamic> toJson() {
    return {
      'item_type': itemType.toJson(),
      'item_id': itemId,
    };
  }
}
