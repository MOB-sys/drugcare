import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'package:pillright/core/providers/service_providers.dart';
import 'package:pillright/features/result/models/interaction_check_response.dart';
import 'package:pillright/features/result/models/interaction_item.dart';
import 'package:pillright/features/search/models/selected_search_item.dart';

/// 상호작용 체크 결과 프로바이더.
///
/// [SelectedSearchItem] 목록을 받아 [InteractionItem]으로 변환한 뒤
/// 상호작용 API를 호출하여 [InteractionCheckResponse]를 반환한다.
final interactionResultProvider = FutureProvider.autoDispose.family<
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
