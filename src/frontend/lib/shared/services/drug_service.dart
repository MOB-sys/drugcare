import 'package:dio/dio.dart';

import 'package:yakmeogeo/core/constants/api_constants.dart';
import 'package:yakmeogeo/core/utils/api_response_parser.dart';
import 'package:yakmeogeo/features/search/models/drug_detail.dart';
import 'package:yakmeogeo/features/search/models/drug_search_item.dart';
import 'package:yakmeogeo/shared/models/paginated_result.dart';

/// 약물 관련 API 서비스.
class DrugService {
  /// Dio HTTP 클라이언트.
  final Dio _dio;

  /// [DrugService] 생성자.
  DrugService(this._dio);

  /// 약물을 검색한다.
  ///
  /// [query] 검색어, [page] 페이지 번호, [pageSize] 페이지 크기.
  Future<PaginatedResult<DrugSearchItem>> searchDrugs(
    String? query, {
    int page = 1,
    int pageSize = 20,
  }) async {
    final response = await _dio.get(
      ApiConstants.drugSearch,
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
        DrugSearchItem.fromJson,
      ),
    );
  }

  /// 약물 상세 정보를 조회한다.
  ///
  /// [drugId] 약물 ID.
  Future<DrugDetail> getDrugDetail(int drugId) async {
    final response = await _dio.get(ApiConstants.drugDetail(drugId));

    return ApiResponseParser.parse(
      response.data as Map<String, dynamic>,
      (data) => DrugDetail.fromJson(data as Map<String, dynamic>),
    );
  }
}
