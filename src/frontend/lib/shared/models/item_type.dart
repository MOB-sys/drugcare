/// 아이템 유형 (의약품 / 영양제 / 식품 / 한약재).
enum ItemType {
  /// 의약품.
  drug,

  /// 영양제.
  supplement,

  /// 식품.
  food,

  /// 한약재.
  herbal;

  /// JSON 문자열로 변환한다.
  String toJson() => name;

  /// JSON 문자열에서 [ItemType]을 생성한다.
  static ItemType fromJson(String value) {
    return ItemType.values.firstWhere(
      (e) => e.name == value,
      orElse: () => throw ArgumentError('Unknown ItemType: $value'),
    );
  }
}
