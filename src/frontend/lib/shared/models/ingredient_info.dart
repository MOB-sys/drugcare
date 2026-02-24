/// 성분 정보 모델.
class IngredientInfo {
  /// 성분명.
  final String name;

  /// 함량.
  final String? amount;

  /// 단위.
  final String? unit;

  /// [IngredientInfo] 생성자.
  const IngredientInfo({
    required this.name,
    this.amount,
    this.unit,
  });

  /// JSON에서 [IngredientInfo]를 생성한다.
  factory IngredientInfo.fromJson(Map<String, dynamic> json) {
    return IngredientInfo(
      name: json['name'] as String,
      amount: json['amount'] as String?,
      unit: json['unit'] as String?,
    );
  }

  /// JSON으로 변환한다.
  Map<String, dynamic> toJson() {
    return {
      'name': name,
      'amount': amount,
      'unit': unit,
    };
  }
}
