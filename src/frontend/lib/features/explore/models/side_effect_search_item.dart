/// 부작용 검색 결과 아이템.
class SideEffectSearchItem {
  /// 약물 ID.
  final int id;

  /// 약물명.
  final String itemName;

  /// 제조사명.
  final String? entpName;

  /// 부작용 텍스트.
  final String? seQesitm;

  /// 약물 이미지 URL.
  final String? itemImage;

  /// SEO slug.
  final String? slug;

  /// [SideEffectSearchItem] 생성자.
  const SideEffectSearchItem({
    required this.id,
    required this.itemName,
    this.entpName,
    this.seQesitm,
    this.itemImage,
    this.slug,
  });

  /// JSON에서 [SideEffectSearchItem]을 생성한다.
  factory SideEffectSearchItem.fromJson(Map<String, dynamic> json) {
    return SideEffectSearchItem(
      id: json['id'] as int,
      itemName: json['item_name'] as String,
      entpName: json['entp_name'] as String?,
      seQesitm: json['se_qesitm'] as String?,
      itemImage: json['item_image'] as String?,
      slug: json['slug'] as String?,
    );
  }
}
