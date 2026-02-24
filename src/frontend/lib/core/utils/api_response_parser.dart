/// API 표준 응답 `{ success, data, error, meta }` 파싱 유틸.
class ApiResponseParser {
  ApiResponseParser._();

  /// API 응답 JSON에서 data 필드를 추출한다.
  ///
  /// [json] 은 `{ "success": bool, "data": T, "error": ..., "meta": ... }` 형태.
  /// [fromJson] 은 data 필드를 원하는 타입으로 변환하는 콜백.
  /// 실패 시 [ApiException]을 throw한다.
  static T parse<T>(
    Map<String, dynamic> json,
    T Function(dynamic data) fromJson,
  ) {
    final success = json['success'] as bool? ?? false;

    if (!success) {
      final error = json['error']?.toString() ?? '알 수 없는 오류가 발생했습니다.';
      throw ApiException(error);
    }

    return fromJson(json['data']);
  }

  /// API 응답 JSON에서 data 필드를 리스트로 추출한다.
  static List<T> parseList<T>(
    Map<String, dynamic> json,
    T Function(Map<String, dynamic>) fromJson,
  ) {
    return parse<List<T>>(
      json,
      (data) => (data as List).map((e) => fromJson(e as Map<String, dynamic>)).toList(),
    );
  }
}

/// API 호출 실패 시 발생하는 예외.
class ApiException implements Exception {
  /// 에러 메시지.
  final String message;

  /// [message] 에러 메시지.
  const ApiException(this.message);

  @override
  String toString() => 'ApiException: $message';
}
