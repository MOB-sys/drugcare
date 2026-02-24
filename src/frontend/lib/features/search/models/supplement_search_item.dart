/// 영양제 검색 결과 아이템.
class SupplementSearchItem {
  /// 영양제 ID.
  final int id;

  /// 제품명.
  final String productName;

  /// 제조사.
  final String? company;

  /// 주성분.
  final String? mainIngredient;

  /// 카테고리.
  final String? category;

  /// [SupplementSearchItem] 생성자.
  const SupplementSearchItem({
    required this.id,
    required this.productName,
    this.company,
    this.mainIngredient,
    this.category,
  });

  /// JSON에서 [SupplementSearchItem]을 생성한다.
  factory SupplementSearchItem.fromJson(Map<String, dynamic> json) {
    return SupplementSearchItem(
      id: json['id'] as int,
      productName: json['product_name'] as String,
      company: json['company'] as String?,
      mainIngredient: json['main_ingredient'] as String?,
      category: json['category'] as String?,
    );
  }
}
