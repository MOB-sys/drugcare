import 'package:dio/dio.dart';

import 'package:pillright/core/constants/api_constants.dart';
import 'package:pillright/core/utils/api_response_parser.dart';

/// 피드백 API 서비스.
class FeedbackService {
  /// Dio HTTP 클라이언트.
  final Dio _dio;

  /// [FeedbackService] 생성자.
  FeedbackService(this._dio);

  /// 피드백을 제출한다.
  ///
  /// [category] 피드백 카테고리 (bug, feature, data_error, other).
  /// [content] 피드백 내용.
  /// [appVersion] 앱 버전.
  /// [osInfo] OS 정보.
  Future<Map<String, dynamic>> submit({
    required String category,
    required String content,
    String appVersion = '1.0.0',
    String? osInfo,
  }) async {
    final response = await _dio.post(
      ApiConstants.feedback,
      data: {
        'category': category,
        'content': content,
        'app_version': appVersion,
        'os_info': osInfo,
      },
    );

    return ApiResponseParser.parse(
      response.data as Map<String, dynamic>,
      (data) => data as Map<String, dynamic>,
    );
  }
}
