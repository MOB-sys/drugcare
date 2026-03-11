/// 식품 상세 정보.
class FoodDetail {
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

  /// 영양 성분.
  final String? nutrients;

  /// 주의사항.
  final String? precautions;

  /// 상호작용 정보.
  final String? interactions;

  /// 이미지 URL.
  final String? imageUrl;

  /// 데이터 출처.
  final String? source;

  /// [FoodDetail] 생성자.
  const FoodDetail({
    required this.id,
    required this.name,
    this.slug,
    this.category,
    this.description,
    this.commonNames,
    this.nutrients,
    this.precautions,
    this.interactions,
    this.imageUrl,
    this.source,
  });

  /// JSON에서 [FoodDetail]을 생성한다.
  factory FoodDetail.fromJson(Map<String, dynamic> json) {
    return FoodDetail(
      id: json['id'] as int,
      name: json['name'] as String,
      slug: json['slug'] as String?,
      category: json['category'] as String?,
      description: json['description'] as String?,
      commonNames: (json['common_names'] as List?)
          ?.map((e) => e as String)
          .toList(),
      nutrients: json['nutrients'] as String?,
      precautions: json['precautions'] as String?,
      interactions: json['interactions'] as String?,
      imageUrl: json['image_url'] as String?,
      source: json['source'] as String?,
    );
  }
}
