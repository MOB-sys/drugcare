/// 질환별 주의약물 검색 결과 아이템.
class ConditionSearchItem {
  /// 약물 ID.
  final int id;

  /// 약물명.
  final String itemName;

  /// 제조사명.
  final String? entpName;

  /// 주의사항 경고 텍스트.
  final String? atpnWarnQesitm;

  /// 주의사항 텍스트.
  final String? atpnQesitm;

  /// 약물 이미지 URL.
  final String? itemImage;

  /// SEO slug.
  final String? slug;

  /// [ConditionSearchItem] 생성자.
  const ConditionSearchItem({
    required this.id,
    required this.itemName,
    this.entpName,
    this.atpnWarnQesitm,
    this.atpnQesitm,
    this.itemImage,
    this.slug,
  });

  /// JSON에서 [ConditionSearchItem]을 생성한다.
  factory ConditionSearchItem.fromJson(Map<String, dynamic> json) {
    return ConditionSearchItem(
      id: json['id'] as int,
      itemName: json['item_name'] as String,
      entpName: json['entp_name'] as String?,
      atpnWarnQesitm: json['atpn_warn_qesitm'] as String?,
      atpnQesitm: json['atpn_qesitm'] as String?,
      itemImage: json['item_image'] as String?,
      slug: json['slug'] as String?,
    );
  }
}
