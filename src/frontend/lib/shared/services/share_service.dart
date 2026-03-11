import 'package:share_plus/share_plus.dart';

/// 공유 서비스.
class ShareService {
  ShareService._();

  /// 상호작용 결과를 공유한다.
  ///
  /// [itemNames] 체크한 아이템 이름 목록.
  /// [interactionsFound] 발견된 상호작용 수.
  /// [hasDanger] 위험 상호작용 존재 여부.
  static Future<void> shareInteractionResult({
    required List<String> itemNames,
    required int interactionsFound,
    required bool hasDanger,
  }) async {
    final itemsText = itemNames.join(', ');
    final emoji = hasDanger ? '⚠️' : '✅';
    final statusText =
        hasDanger ? '주의가 필요한 상호작용이 있습니다' : '안전한 조합입니다';

    final text = '$emoji 약잘알 상호작용 체크 결과\n\n'
        '체크 항목: $itemsText\n'
        '상호작용: $interactionsFound건 발견\n'
        '결과: $statusText\n\n'
        '약잘알에서 무료로 확인하세요!\n'
        'https://pillright.com';

    await Share.share(text);
  }

  /// 약물/영양제 정보를 공유한다.
  static Future<void> shareDrugInfo({
    required String name,
    required String type,
    required int id,
  }) async {
    final typeLabel = type == 'drug' ? '약물' : '영양제';
    final text = '💊 $typeLabel 정보: $name\n\n'
        '약잘알에서 상세 정보와 상호작용을 확인하세요!\n'
        'https://pillright.com';

    await Share.share(text);
  }
}
