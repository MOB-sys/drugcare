/// DUR 안전성 정보 항목.
class DURSafetyItem {
  /// DUR 유형 코드.
  final String durType;

  /// 유형명.
  final String typeName;

  /// 성분명.
  final String? ingrName;

  /// 금기 내용.
  final String? prohibitionContent;

  /// 비고.
  final String? remark;

  /// [DURSafetyItem] 생성자.
  const DURSafetyItem({
    required this.durType,
    required this.typeName,
    this.ingrName,
    this.prohibitionContent,
    this.remark,
  });

  /// JSON에서 [DURSafetyItem]을 생성한다.
  factory DURSafetyItem.fromJson(Map<String, dynamic> json) {
    return DURSafetyItem(
      durType: json['dur_type'] as String,
      typeName: json['type_name'] as String,
      ingrName: json['ingr_name'] as String?,
      prohibitionContent: json['prohibition_content'] as String?,
      remark: json['remark'] as String?,
    );
  }
}
