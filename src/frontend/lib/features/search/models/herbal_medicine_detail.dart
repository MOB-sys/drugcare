/// 한약재 상세 정보.
class HerbalMedicineDetail {
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

  /// 용법·용량.
  final String? dosage;

  /// 주의사항.
  final String? precautions;

  /// 상호작용 정보.
  final String? interactions;

  /// 이미지 URL.
  final String? imageUrl;

  /// 데이터 출처.
  final String? source;

  /// [HerbalMedicineDetail] 생성자.
  const HerbalMedicineDetail({
    required this.id,
    required this.name,
    this.slug,
    this.koreanName,
    this.latinName,
    this.category,
    this.description,
    this.efficacy,
    this.dosage,
    this.precautions,
    this.interactions,
    this.imageUrl,
    this.source,
  });

  /// JSON에서 [HerbalMedicineDetail]을 생성한다.
  factory HerbalMedicineDetail.fromJson(Map<String, dynamic> json) {
    return HerbalMedicineDetail(
      id: json['id'] as int,
      name: json['name'] as String,
      slug: json['slug'] as String?,
      koreanName: json['korean_name'] as String?,
      latinName: json['latin_name'] as String?,
      category: json['category'] as String?,
      description: json['description'] as String?,
      efficacy: json['efficacy'] as String?,
      dosage: json['dosage'] as String?,
      precautions: json['precautions'] as String?,
      interactions: json['interactions'] as String?,
      imageUrl: json['image_url'] as String?,
      source: json['source'] as String?,
    );
  }
}
