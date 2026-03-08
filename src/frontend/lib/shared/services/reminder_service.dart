import 'package:dio/dio.dart';

import 'package:pillright/core/constants/api_constants.dart';
import 'package:pillright/core/utils/api_response_parser.dart';
import 'package:pillright/features/reminder/models/reminder.dart';

/// 리마인더 관련 API 서비스.
class ReminderService {
  /// Dio HTTP 클라이언트.
  final Dio _dio;

  /// [ReminderService] 생성자.
  ReminderService(this._dio);

  /// 리마인더를 생성한다.
  ///
  /// [reminder] 생성할 리마인더 정보.
  Future<Reminder> createReminder(ReminderCreate reminder) async {
    final response = await _dio.post(
      ApiConstants.reminders,
      data: reminder.toJson(),
    );

    return ApiResponseParser.parse(
      response.data as Map<String, dynamic>,
      (data) => Reminder.fromJson(data as Map<String, dynamic>),
    );
  }

  /// 리마인더 목록을 조회한다.
  ///
  /// [activeOnly] true면 활성 리마인더만 조회.
  Future<List<Reminder>> listReminders({bool activeOnly = true}) async {
    final response = await _dio.get(
      ApiConstants.reminders,
      queryParameters: {'active_only': activeOnly},
    );

    return ApiResponseParser.parseList(
      response.data as Map<String, dynamic>,
      Reminder.fromJson,
    );
  }

  /// 리마인더를 수정한다.
  ///
  /// [reminderId] 수정할 리마인더 ID, [update] 수정 내용.
  Future<Reminder> updateReminder(
    int reminderId,
    ReminderUpdate update,
  ) async {
    final response = await _dio.patch(
      ApiConstants.reminder(reminderId),
      data: update.toJson(),
    );

    return ApiResponseParser.parse(
      response.data as Map<String, dynamic>,
      (data) => Reminder.fromJson(data as Map<String, dynamic>),
    );
  }

  /// 리마인더를 삭제한다.
  ///
  /// [reminderId] 삭제할 리마인더 ID.
  Future<void> deleteReminder(int reminderId) async {
    final response = await _dio.delete(ApiConstants.reminder(reminderId));

    ApiResponseParser.parse(
      response.data as Map<String, dynamic>,
      (data) => null,
    );
  }
}
