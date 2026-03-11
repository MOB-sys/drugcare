import 'package:pillright/features/detail/models/dur_safety_item.dart';
import 'package:pillright/shared/models/ingredient_info.dart';

/// 약물 상세 정보.
class DrugDetail {
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

  /// 성상.
  final String? chart;

  /// 바코드.
  final String? barCode;

  /// 원료성분.
  final String? materialName;

  /// 성분 목록.
  final List<IngredientInfo>? ingredients;

  /// 효능효과.
  final String? efcyQesitm;

  /// 용법용량.
  final String? useMethodQesitm;

  /// 주의사항 경고.
  final String? atpnWarnQesitm;

  /// 주의사항.
  final String? atpnQesitm;

  /// 상호작용.
  final String? intrcQesitm;

  /// 부작용.
  final String? seQesitm;

  /// 보관법.
  final String? depositMethodQesitm;

  /// 약물 이미지 URL.
  final String? itemImage;

  /// DUR 안전성 정보 목록.
  final List<DURSafetyItem>? durSafety;

  /// [DrugDetail] 생성자.
  const DrugDetail({
    required this.id,
    required this.itemSeq,
    required this.itemName,
    this.entpName,
    this.etcOtcCode,
    this.classNo,
    this.chart,
    this.barCode,
    this.materialName,
    this.ingredients,
    this.efcyQesitm,
    this.useMethodQesitm,
    this.atpnWarnQesitm,
    this.atpnQesitm,
    this.intrcQesitm,
    this.seQesitm,
    this.depositMethodQesitm,
    this.itemImage,
    this.durSafety,
  });

  /// JSON에서 [DrugDetail]을 생성한다.
  factory DrugDetail.fromJson(Map<String, dynamic> json) {
    return DrugDetail(
      id: json['id'] as int,
      itemSeq: json['item_seq'] as String,
      itemName: json['item_name'] as String,
      entpName: json['entp_name'] as String?,
      etcOtcCode: json['etc_otc_code'] as String?,
      classNo: json['class_no'] as String?,
      chart: json['chart'] as String?,
      barCode: json['bar_code'] as String?,
      materialName: json['material_name'] as String?,
      ingredients: (json['ingredients'] as List?)
          ?.map((e) => IngredientInfo.fromJson(e as Map<String, dynamic>))
          .toList(),
      efcyQesitm: json['efcy_qesitm'] as String?,
      useMethodQesitm: json['use_method_qesitm'] as String?,
      atpnWarnQesitm: json['atpn_warn_qesitm'] as String?,
      atpnQesitm: json['atpn_qesitm'] as String?,
      intrcQesitm: json['intrc_qesitm'] as String?,
      seQesitm: json['se_qesitm'] as String?,
      depositMethodQesitm: json['deposit_method_qesitm'] as String?,
      itemImage: json['item_image'] as String?,
      durSafety: (json['dur_safety'] as List?)
          ?.map((e) => DURSafetyItem.fromJson(e as Map<String, dynamic>))
          .toList(),
    );
  }
}
