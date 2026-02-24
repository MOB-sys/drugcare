import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'package:yakmeogeo/core/providers/service_providers.dart';
import 'package:yakmeogeo/features/cabinet/models/cabinet_item.dart';

/// 홈 화면 복약함 요약 프로바이더.
///
/// 복약함 서비스에서 아이템 목록을 가져와 홈 화면에 요약 표시한다.
final homeCabinetSummaryProvider =
    FutureProvider<List<CabinetItem>>((ref) async {
  final cabinetService = ref.read(cabinetServiceProvider);
  return cabinetService.listItems();
});
