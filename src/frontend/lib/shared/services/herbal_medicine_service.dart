import 'package:dio/dio.dart';

import 'package:pillright/core/constants/api_constants.dart';
import 'package:pillright/core/utils/api_response_parser.dart';
import 'package:pillright/features/search/models/herbal_medicine_detail.dart';
import 'package:pillright/features/search/models/herbal_medicine_search_item.dart';
import 'package:pillright/shared/models/paginated_result.dart';

/// 한약재 관련 API 서비스.
class HerbalMedicineService {
  /// Dio HTTP 클라이언트.
  final Dio _dio;

  /// [HerbalMedicineService] 생성자.
  HerbalMedicineService(this._dio);

  /// 한약재를 검색한다.
  ///
  /// [query] 검색어, [page] 페이지 번호, [pageSize] 페이지 크기.
  Future<PaginatedResult<HerbalMedicineSearchItem>> searchHerbalMedicines(
    String? query, {
    int page = 1,
    int pageSize = 20,
  }) async {
    final response = await _dio.get(
      ApiConstants.herbalMedicineSearch,
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
        HerbalMedicineSearchItem.fromJson,
      ),
    );
  }

  /// 한약재 상세 정보를 조회한다.
  ///
  /// [herbalMedicineId] 한약재 ID.
  Future<HerbalMedicineDetail> getHerbalMedicineDetail(
    int herbalMedicineId,
  ) async {
    final response = await _dio.get(
      ApiConstants.herbalMedicineDetail(herbalMedicineId),
    );

    return ApiResponseParser.parse(
      response.data as Map<String, dynamic>,
      (data) => HerbalMedicineDetail.fromJson(data as Map<String, dynamic>),
    );
  }

  /// 슬러그로 한약재 상세 정보를 조회한다.
  ///
  /// [slug] 한약재 슬러그.
  Future<HerbalMedicineDetail> getHerbalMedicineBySlug(String slug) async {
    final response = await _dio.get(
      ApiConstants.herbalMedicineBySlug(slug),
    );

    return ApiResponseParser.parse(
      response.data as Map<String, dynamic>,
      (data) => HerbalMedicineDetail.fromJson(data as Map<String, dynamic>),
    );
  }
}
