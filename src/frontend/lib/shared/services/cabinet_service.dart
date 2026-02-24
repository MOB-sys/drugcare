import 'package:dio/dio.dart';

import 'package:yakmeogeo/core/constants/api_constants.dart';
import 'package:yakmeogeo/core/utils/api_response_parser.dart';
import 'package:yakmeogeo/features/cabinet/models/cabinet_item.dart';

/// 복약함 관련 API 서비스.
class CabinetService {
  /// Dio HTTP 클라이언트.
  final Dio _dio;

  /// [CabinetService] 생성자.
  CabinetService(this._dio);

  /// 복약함에 아이템을 추가한다.
  ///
  /// [item] 추가할 아이템 정보.
  Future<CabinetItem> addItem(CabinetItemCreate item) async {
    final response = await _dio.post(
      ApiConstants.cabinet,
      data: item.toJson(),
    );

    return ApiResponseParser.parse(
      response.data as Map<String, dynamic>,
      (data) => CabinetItem.fromJson(data as Map<String, dynamic>),
    );
  }

  /// 복약함 아이템 목록을 조회한다.
  Future<List<CabinetItem>> listItems() async {
    final response = await _dio.get(ApiConstants.cabinet);

    return ApiResponseParser.parseList(
      response.data as Map<String, dynamic>,
      CabinetItem.fromJson,
    );
  }

  /// 복약함에서 아이템을 삭제한다.
  ///
  /// [itemId] 삭제할 아이템 ID.
  Future<void> deleteItem(int itemId) async {
    final response = await _dio.delete(ApiConstants.cabinetItem(itemId));

    ApiResponseParser.parse(
      response.data as Map<String, dynamic>,
      (data) => null,
    );
  }
}
