/// 약물 검색 결과 아이템.
class DrugSearchItem {
  /// 약물 ID.
  final int id;

  /// 품목일련번호.
  final String itemSeq;

  /// 품목명.
  final String itemName;

  /// 업체명.
  final String? entpName;

  /// 전문/일반 구분코드.
  final String? etcOtcCode;

  /// 분류번호.
  final String? classNo;

  /// 약물 이미지 URL.
  final String? itemImage;

  /// [DrugSearchItem] 생성자.
  const DrugSearchItem({
    required this.id,
    required this.itemSeq,
    required this.itemName,
    this.entpName,
    this.etcOtcCode,
    this.classNo,
    this.itemImage,
  });

  /// JSON에서 [DrugSearchItem]을 생성한다.
  factory DrugSearchItem.fromJson(Map<String, dynamic> json) {
    return DrugSearchItem(
      id: json['id'] as int,
      itemSeq: json['item_seq'] as String,
      itemName: json['item_name'] as String,
      entpName: json['entp_name'] as String?,
      etcOtcCode: json['etc_otc_code'] as String?,
      classNo: json['class_no'] as String?,
      itemImage: json['item_image'] as String?,
    );
  }
}
