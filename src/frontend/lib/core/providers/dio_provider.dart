import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../constants/api_constants.dart';
import 'device_id_provider.dart';

/// Dio HTTP 클라이언트 프로바이더.
///
/// X-Device-ID 인터셉터와 로깅 인터셉터를 자동 등록한다.
final dioProvider = Provider<Dio>((ref) {
  final deviceId = ref.read(deviceIdProvider);

  final dio = Dio(
    BaseOptions(
      baseUrl: ApiConstants.baseUrl,
      connectTimeout: const Duration(seconds: 10),
      receiveTimeout: const Duration(seconds: 10),
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
    ),
  );

  // X-Device-ID 자동 주입 인터셉터
  dio.interceptors.add(
    InterceptorsWrapper(
      onRequest: (options, handler) {
        options.headers[ApiConstants.deviceIdHeader] = deviceId;
        handler.next(options);
      },
    ),
  );

  // 디버그 로깅 인터셉터
  if (kDebugMode) {
    dio.interceptors.add(
      LogInterceptor(
        requestBody: true,
        responseBody: true,
        logPrint: (obj) => debugPrint(obj.toString()),
      ),
    );
  }

  return dio;
});
