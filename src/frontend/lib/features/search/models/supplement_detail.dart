/// 영양제 상세 정보.
class SupplementDetail {
  /// 영양제 ID.
  final int id;

  /// 제품명.
  final String productName;

  /// 제조사.
  final String? company;

  /// 신고번호.
  final String? registrationNo;

  /// 주성분.
  final String? mainIngredient;

  /// 성분 목록 (원본 JSON 구조).
  final List<Map<String, dynamic>>? ingredients;

  /// 기능성.
  final String? functionality;

  /// 주의사항.
  final String? precautions;

  /// 섭취방법.
  final String? intakeMethod;

  /// 카테고리.
  final String? category;

  /// 데이터 출처.
  final String? source;

  /// [SupplementDetail] 생성자.
  const SupplementDetail({
    required this.id,
    required this.productName,
    this.company,
    this.registrationNo,
    this.mainIngredient,
    this.ingredients,
    this.functionality,
    this.precautions,
    this.intakeMethod,
    this.category,
    this.source,
  });

  /// JSON에서 [SupplementDetail]을 생성한다.
  factory SupplementDetail.fromJson(Map<String, dynamic> json) {
    return SupplementDetail(
      id: json['id'] as int,
      productName: json['product_name'] as String,
      company: json['company'] as String?,
      registrationNo: json['registration_no'] as String?,
      mainIngredient: json['main_ingredient'] as String?,
      ingredients: (json['ingredients'] as List?)
          ?.map((e) => Map<String, dynamic>.from(e as Map))
          .toList(),
      functionality: json['functionality'] as String?,
      precautions: json['precautions'] as String?,
      intakeMethod: json['intake_method'] as String?,
      category: json['category'] as String?,
      source: json['source'] as String?,
    );
  }
}
