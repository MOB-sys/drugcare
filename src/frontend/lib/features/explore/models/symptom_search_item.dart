/// 증상 검색 결과 아이템.
class SymptomSearchItem {
  /// 약물 ID.
  final int id;

  /// 약물명.
  final String itemName;

  /// 제조사명.
  final String? entpName;

  /// 효능·효과 텍스트.
  final String? efcyQesitm;

  /// 약물 이미지 URL.
  final String? itemImage;

  /// SEO slug.
  final String? slug;

  /// [SymptomSearchItem] 생성자.
  const SymptomSearchItem({
    required this.id,
    required this.itemName,
    this.entpName,
    this.efcyQesitm,
    this.itemImage,
    this.slug,
  });

  /// JSON에서 [SymptomSearchItem]을 생성한다.
  factory SymptomSearchItem.fromJson(Map<String, dynamic> json) {
    return SymptomSearchItem(
      id: json['id'] as int,
      itemName: json['item_name'] as String,
      entpName: json['entp_name'] as String?,
      efcyQesitm: json['efcy_qesitm'] as String?,
      itemImage: json['item_image'] as String?,
      slug: json['slug'] as String?,
    );
  }
}
