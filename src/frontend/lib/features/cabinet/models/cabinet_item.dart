import 'package:yakmeogeo/shared/models/item_type.dart';

/// 복약함 아이템 (서버 응답).
class CabinetItem {
  /// 아이템 ID.
  final int id;

  /// 디바이스 ID.
  final String deviceId;

  /// 아이템 유형 (약물/영양제).
  final ItemType itemType;

  /// 원본 아이템 ID.
  final int itemId;

  /// 아이템 이름.
  final String itemName;

  /// 별칭.
  final String? nickname;

  /// 생성 일시.
  final DateTime createdAt;

  /// [CabinetItem] 생성자.
  const CabinetItem({
    required this.id,
    required this.deviceId,
    required this.itemType,
    required this.itemId,
    required this.itemName,
    this.nickname,
    required this.createdAt,
  });

  /// JSON에서 [CabinetItem]을 생성한다.
  factory CabinetItem.fromJson(Map<String, dynamic> json) {
    return CabinetItem(
      id: json['id'] as int,
      deviceId: json['device_id'] as String,
      itemType: ItemType.fromJson(json['item_type'] as String),
      itemId: json['item_id'] as int,
      itemName: json['item_name'] as String,
      nickname: json['nickname'] as String?,
      createdAt: DateTime.parse(json['created_at'] as String),
    );
  }
}

/// 복약함 아이템 생성 요청.
class CabinetItemCreate {
  /// 아이템 유형 (약물/영양제).
  final ItemType itemType;

  /// 아이템 ID.
  final int itemId;

  /// 별칭.
  final String? nickname;

  /// [CabinetItemCreate] 생성자.
  const CabinetItemCreate({
    required this.itemType,
    required this.itemId,
    this.nickname,
  });

  /// JSON으로 변환한다.
  Map<String, dynamic> toJson() {
    return {
      'item_type': itemType.toJson(),
      'item_id': itemId,
      'nickname': nickname,
    };
  }
}
