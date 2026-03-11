import 'package:dio/dio.dart';
import 'package:pillright/core/constants/api_constants.dart';

/// 앱 이벤트 분석 서비스.
///
/// Fire-and-forget 패턴 — 실패 시 무시한다.
class MetricsService {
  final Dio _dio;

  /// [MetricsService] 생성자.
  MetricsService(this._dio);

  /// 이벤트를 기록한다.
  ///
  /// [eventType] 이벤트 유형 (예: app_open, interaction_check).
  /// [eventData] 추가 데이터 (선택).
  Future<void> trackEvent(
    String eventType, {
    Map<String, dynamic>? eventData,
  }) async {
    try {
      await _dio.post(
        ApiConstants.metrics,
        data: {
          'event_type': eventType,
          if (eventData != null) 'event_data': eventData,
        },
      );
    } catch (_) {
      // Fire-and-forget — 분석 실패는 무시.
    }
  }
}
