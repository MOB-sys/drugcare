/// 한약재 검색 결과 아이템.
class HerbalMedicineSearchItem {
  /// 한약재 ID.
  final int id;

  /// 한약재명.
  final String name;

  /// 슬러그.
  final String? slug;

  /// 한글명.
  final String? koreanName;

  /// 라틴명.
  final String? latinName;

  /// 카테고리.
  final String? category;

  /// 설명.
  final String? description;

  /// 효능.
  final String? efficacy;

  /// 이미지 URL.
  final String? imageUrl;

  /// [HerbalMedicineSearchItem] 생성자.
  const HerbalMedicineSearchItem({
    required this.id,
    required this.name,
    this.slug,
    this.koreanName,
    this.latinName,
    this.category,
    this.description,
    this.efficacy,
    this.imageUrl,
  });

  /// JSON에서 [HerbalMedicineSearchItem]을 생성한다.
  factory HerbalMedicineSearchItem.fromJson(Map<String, dynamic> json) {
    return HerbalMedicineSearchItem(
      id: json['id'] as int,
      name: json['name'] as String,
      slug: json['slug'] as String?,
      koreanName: json['korean_name'] as String?,
      latinName: json['latin_name'] as String?,
      category: json['category'] as String?,
      description: json['description'] as String?,
      efficacy: json['efficacy'] as String?,
      imageUrl: json['image_url'] as String?,
    );
  }
}
