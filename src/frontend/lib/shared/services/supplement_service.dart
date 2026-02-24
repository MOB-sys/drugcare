import 'package:dio/dio.dart';

import 'package:yakmeogeo/core/constants/api_constants.dart';
import 'package:yakmeogeo/core/utils/api_response_parser.dart';
import 'package:yakmeogeo/features/search/models/supplement_detail.dart';
import 'package:yakmeogeo/features/search/models/supplement_search_item.dart';
import 'package:yakmeogeo/shared/models/paginated_result.dart';

/// 영양제 관련 API 서비스.
class SupplementService {
  /// Dio HTTP 클라이언트.
  final Dio _dio;

  /// [SupplementService] 생성자.
  SupplementService(this._dio);

  /// 영양제를 검색한다.
  ///
  /// [query] 검색어, [page] 페이지 번호, [pageSize] 페이지 크기.
  Future<PaginatedResult<SupplementSearchItem>> searchSupplements(
    String? query, {
    int page = 1,
    int pageSize = 20,
  }) async {
    final response = await _dio.get(
      ApiConstants.supplementSearch,
      queryParameters: {
        if (query != null && query.isNotEmpty) 'query': query,
        'page': page,
        'page_size': pageSize,
      },
    );

    return ApiResponseParser.parse(
      response.data as Map<String, dynamic>,
      (data) => PaginatedResult.fromJson(
        data as Map<String, dynamic>,
        SupplementSearchItem.fromJson,
      ),
    );
  }

  /// 영양제 상세 정보를 조회한다.
  ///
  /// [supplementId] 영양제 ID.
  Future<SupplementDetail> getSupplementDetail(int supplementId) async {
    final response = await _dio.get(
      ApiConstants.supplementDetail(supplementId),
    );

    return ApiResponseParser.parse(
      response.data as Map<String, dynamic>,
      (data) => SupplementDetail.fromJson(data as Map<String, dynamic>),
    );
  }
}
