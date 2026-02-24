import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'package:yakmeogeo/core/providers/service_providers.dart';
import 'package:yakmeogeo/features/result/models/interaction_check_response.dart';
import 'package:yakmeogeo/features/result/models/interaction_item.dart';
import 'package:yakmeogeo/features/search/models/selected_search_item.dart';

/// 상호작용 체크 결과 프로바이더.
///
/// [SelectedSearchItem] 목록을 받아 [InteractionItem]으로 변환한 뒤
/// 상호작용 API를 호출하여 [InteractionCheckResponse]를 반환한다.
final interactionResultProvider = FutureProvider.family<
    InteractionCheckResponse, List<SelectedSearchItem>>(
  (ref, selectedItems) async {
    final interactionService = ref.read(interactionServiceProvider);

    final items = selectedItems
        .map(
          (e) => InteractionItem(
            itemType: e.itemType,
            itemId: e.itemId,
          ),
        )
        .toList();

    return interactionService.checkInteractions(items);
  },
);
