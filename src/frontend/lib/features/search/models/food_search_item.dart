/// 식품 검색 결과 아이템.
class FoodSearchItem {
  /// 식품 ID.
  final int id;

  /// 식품명.
  final String name;

  /// 슬러그.
  final String? slug;

  /// 카테고리.
  final String? category;

  /// 설명.
  final String? description;

  /// 일반명 목록.
  final List<String>? commonNames;

  /// 이미지 URL.
  final String? imageUrl;

  /// [FoodSearchItem] 생성자.
  const FoodSearchItem({
    required this.id,
    required this.name,
    this.slug,
    this.category,
    this.description,
    this.commonNames,
    this.imageUrl,
  });

  /// JSON에서 [FoodSearchItem]을 생성한다.
  factory FoodSearchItem.fromJson(Map<String, dynamic> json) {
    return FoodSearchItem(
      id: json['id'] as int,
      name: json['name'] as String,
      slug: json['slug'] as String?,
      category: json['category'] as String?,
      description: json['description'] as String?,
      commonNames: (json['common_names'] as List?)
          ?.map((e) => e as String)
          .toList(),
      imageUrl: json['image_url'] as String?,
    );
  }
}
