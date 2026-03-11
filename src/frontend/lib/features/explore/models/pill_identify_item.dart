/// 알약 식별 결과 아이템.
class PillIdentifyItem {
  /// 약물 ID.
  final int id;

  /// 약물명.
  final String itemName;

  /// 제조사명.
  final String? entpName;

  /// 외형 설명 (성상).
  final String? chart;

  /// 약물 이미지 URL.
  final String? itemImage;

  /// 전문/일반 의약품 구분 코드.
  final String? etcOtcCode;

  /// [PillIdentifyItem] 생성자.
  const PillIdentifyItem({
    required this.id,
    required this.itemName,
    this.entpName,
    this.chart,
    this.itemImage,
    this.etcOtcCode,
  });

  /// JSON에서 [PillIdentifyItem]을 생성한다.
  factory PillIdentifyItem.fromJson(Map<String, dynamic> json) {
    return PillIdentifyItem(
      id: json['id'] as int,
      itemName: json['item_name'] as String,
      entpName: json['entp_name'] as String?,
      chart: json['chart'] as String?,
      itemImage: json['item_image'] as String?,
      etcOtcCode: json['etc_otc_code'] as String?,
    );
  }
}
