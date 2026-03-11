import 'package:dio/dio.dart';

import 'package:pillright/core/constants/api_constants.dart';
import 'package:pillright/core/utils/api_response_parser.dart';
import 'package:pillright/features/search/models/food_detail.dart';
import 'package:pillright/features/search/models/food_search_item.dart';
import 'package:pillright/shared/models/paginated_result.dart';

/// 식품 관련 API 서비스.
class FoodService {
  /// Dio HTTP 클라이언트.
  final Dio _dio;

  /// [FoodService] 생성자.
  FoodService(this._dio);

  /// 식품을 검색한다.
  ///
  /// [query] 검색어, [page] 페이지 번호, [pageSize] 페이지 크기.
  Future<PaginatedResult<FoodSearchItem>> searchFoods(
    String? query, {
    int page = 1,
    int pageSize = 20,
  }) async {
    final response = await _dio.get(
      ApiConstants.foodSearch,
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
        FoodSearchItem.fromJson,
      ),
    );
  }

  /// 식품 상세 정보를 조회한다.
  ///
  /// [foodId] 식품 ID.
  Future<FoodDetail> getFoodDetail(int foodId) async {
    final response = await _dio.get(ApiConstants.foodDetail(foodId));

    return ApiResponseParser.parse(
      response.data as Map<String, dynamic>,
      (data) => FoodDetail.fromJson(data as Map<String, dynamic>),
    );
  }

  /// 슬러그로 식품 상세 정보를 조회한다.
  ///
  /// [slug] 식품 슬러그.
  Future<FoodDetail> getFoodBySlug(String slug) async {
    final response = await _dio.get(ApiConstants.foodBySlug(slug));

    return ApiResponseParser.parse(
      response.data as Map<String, dynamic>,
      (data) => FoodDetail.fromJson(data as Map<String, dynamic>),
    );
  }
}
