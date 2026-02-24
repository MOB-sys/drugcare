import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:uuid/uuid.dart';

import '../constants/app_constants.dart';

/// SharedPreferences 인스턴스 프로바이더.
final sharedPreferencesProvider = Provider<SharedPreferences>((ref) {
  throw UnimplementedError('SharedPreferences를 ProviderScope에서 override 해주세요.');
});

/// 디바이스 고유 ID 프로바이더.
///
/// UUID v4를 생성하여 SharedPreferences에 영속화한다.
/// 앱 최초 실행 시 생성되며, 이후 동일 ID를 반환한다.
final deviceIdProvider = Provider<String>((ref) {
  final prefs = ref.read(sharedPreferencesProvider);
  var deviceId = prefs.getString(AppConstants.deviceIdKey);

  if (deviceId == null || deviceId.isEmpty) {
    deviceId = const Uuid().v4();
    prefs.setString(AppConstants.deviceIdKey, deviceId);
  }

  return deviceId;
});
