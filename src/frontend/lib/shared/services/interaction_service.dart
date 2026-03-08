import 'package:dio/dio.dart';

import 'package:pillright/core/constants/api_constants.dart';
import 'package:pillright/core/utils/api_response_parser.dart';
import 'package:pillright/features/result/models/interaction_check_response.dart';
import 'package:pillright/features/result/models/interaction_item.dart';

/// 상호작용 체크 API 서비스.
class InteractionService {
  /// Dio HTTP 클라이언트.
  final Dio _dio;

  /// [InteractionService] 생성자.
  InteractionService(this._dio);

  /// 아이템 목록의 상호작용을 체크한다.
  ///
  /// [items] 체크할 아이템 목록 (최소 2개).
  Future<InteractionCheckResponse> checkInteractions(
    List<InteractionItem> items,
  ) async {
    final response = await _dio.post(
      ApiConstants.interactionCheck,
      data: {
        'items': items.map((e) => e.toJson()).toList(),
      },
    );

    return ApiResponseParser.parse(
      response.data as Map<String, dynamic>,
      (data) =>
          InteractionCheckResponse.fromJson(data as Map<String, dynamic>),
    );
  }
}
