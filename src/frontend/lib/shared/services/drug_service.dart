import 'package:dio/dio.dart';

import 'package:pillright/core/constants/api_constants.dart';
import 'package:pillright/core/utils/api_response_parser.dart';
import 'package:pillright/features/explore/models/condition_search_item.dart';
import 'package:pillright/features/explore/models/pill_identify_item.dart';
import 'package:pillright/features/explore/models/side_effect_search_item.dart';
import 'package:pillright/features/explore/models/symptom_search_item.dart';
import 'package:pillright/features/search/models/drug_detail.dart';
import 'package:pillright/features/search/models/drug_search_item.dart';
import 'package:pillright/shared/models/paginated_result.dart';

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

  /// 증상별 약물을 검색한다.
  ///
  /// [query] 증상 키워드, [page] 페이지 번호, [pageSize] 페이지 크기.
  Future<PaginatedResult<SymptomSearchItem>> searchBySymptom(
    String query, {
    int page = 1,
    int pageSize = 20,
  }) async {
    final response = await _dio.get(
      ApiConstants.drugSymptomSearch,
      queryParameters: {'q': query, 'page': page, 'page_size': pageSize},
    );

    return ApiResponseParser.parse(
      response.data as Map<String, dynamic>,
      (data) => PaginatedResult.fromJson(
        data as Map<String, dynamic>,
        SymptomSearchItem.fromJson,
      ),
    );
  }

  /// 부작용으로 약물을 검색한다.
  ///
  /// [query] 부작용 키워드, [page] 페이지 번호, [pageSize] 페이지 크기.
  Future<PaginatedResult<SideEffectSearchItem>> searchBySideEffect(
    String query, {
    int page = 1,
    int pageSize = 20,
  }) async {
    final response = await _dio.get(
      ApiConstants.drugSideEffectSearch,
      queryParameters: {'q': query, 'page': page, 'page_size': pageSize},
    );

    return ApiResponseParser.parse(
      response.data as Map<String, dynamic>,
      (data) => PaginatedResult.fromJson(
        data as Map<String, dynamic>,
        SideEffectSearchItem.fromJson,
      ),
    );
  }

  /// 알약 외형으로 약물을 식별한다.
  ///
  /// [color] 색상, [shape] 모양, [imprint] 각인 문자.
  Future<PaginatedResult<PillIdentifyItem>> identifyPill({
    String? color,
    String? shape,
    String? imprint,
    int page = 1,
    int pageSize = 20,
  }) async {
    final response = await _dio.get(
      ApiConstants.drugIdentify,
      queryParameters: {
        if (color != null && color.isNotEmpty) 'color': color,
        if (shape != null && shape.isNotEmpty) 'shape': shape,
        if (imprint != null && imprint.isNotEmpty) 'imprint': imprint,
        'page': page,
        'page_size': pageSize,
      },
    );

    return ApiResponseParser.parse(
      response.data as Map<String, dynamic>,
      (data) => PaginatedResult.fromJson(
        data as Map<String, dynamic>,
        PillIdentifyItem.fromJson,
      ),
    );
  }

  /// 질환별 주의 약물을 검색한다.
  ///
  /// [query] 질환 키워드, [page] 페이지 번호, [pageSize] 페이지 크기.
  Future<PaginatedResult<ConditionSearchItem>> searchByCondition(
    String query, {
    int page = 1,
    int pageSize = 20,
  }) async {
    final response = await _dio.get(
      ApiConstants.drugConditionSearch,
      queryParameters: {'q': query, 'page': page, 'page_size': pageSize},
    );

    return ApiResponseParser.parse(
      response.data as Map<String, dynamic>,
      (data) => PaginatedResult.fromJson(
        data as Map<String, dynamic>,
        ConditionSearchItem.fromJson,
      ),
    );
  }
}
