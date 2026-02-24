import 'package:dio/dio.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';
import 'package:yakmeogeo/core/constants/api_constants.dart';
import 'package:yakmeogeo/features/reminder/models/reminder.dart';
import 'package:yakmeogeo/shared/services/reminder_service.dart';

class MockDio extends Mock implements Dio {}

void main() {
  late MockDio mockDio;
  late ReminderService service;

  setUp(() {
    mockDio = MockDio();
    service = ReminderService(mockDio);
  });

  // 리마인더 JSON 팩토리
  Map<String, dynamic> reminderJson({
    int id = 1,
    String itemName = '타이레놀정500밀리그램',
    String reminderTime = '09:00:00',
    List<int> daysOfWeek = const [1, 2, 3, 4, 5],
    bool isActive = true,
  }) =>
      {
        'id': id,
        'device_id': 'test-device-123',
        'cabinet_item_id': 10,
        'item_name': itemName,
        'reminder_time': reminderTime,
        'days_of_week': daysOfWeek,
        'is_active': isActive,
        'memo': null,
        'created_at': '2026-01-15T09:30:00Z',
      };

  group('ReminderService', () {
    group('createReminder', () {
      test('정상 응답 시 Reminder를 반환한다', () async {
        const createData = ReminderCreate(
          cabinetItemId: 10,
          reminderTime: '09:00:00',
          daysOfWeek: [1, 2, 3, 4, 5],
          memo: '아침 식후',
        );

        when(() => mockDio.post(
              any(),
              data: any(named: 'data'),
            )).thenAnswer((_) async => Response(
              data: {
                'success': true,
                'data': {
                  ...reminderJson(),
                  'memo': '아침 식후',
                },
                'error': null,
              },
              statusCode: 201,
              requestOptions: RequestOptions(path: ''),
            ));

        final result = await service.createReminder(createData);

        expect(result.id, 1);
        expect(result.itemName, '타이레놀정500밀리그램');
        expect(result.reminderTime, '09:00:00');
        expect(result.daysOfWeek, [1, 2, 3, 4, 5]);
        expect(result.memo, '아침 식후');
        verify(() => mockDio.post(
              ApiConstants.reminders,
              data: createData.toJson(),
            )).called(1);
      });
    });

    group('listReminders', () {
      test('활성 리마인더만 조회한다', () async {
        when(() => mockDio.get(
              any(),
              queryParameters: any(named: 'queryParameters'),
            )).thenAnswer((_) async => Response(
              data: {
                'success': true,
                'data': [
                  reminderJson(id: 1, isActive: true),
                  reminderJson(id: 2, itemName: '비타민C', isActive: true),
                ],
                'error': null,
              },
              statusCode: 200,
              requestOptions: RequestOptions(path: ''),
            ));

        final result = await service.listReminders();

        expect(result, hasLength(2));
        expect(result.every((r) => r.isActive), true);
        verify(() => mockDio.get(
              ApiConstants.reminders,
              queryParameters: {'active_only': true},
            )).called(1);
      });

      test('모든 리마인더를 조회한다', () async {
        when(() => mockDio.get(
              any(),
              queryParameters: any(named: 'queryParameters'),
            )).thenAnswer((_) async => Response(
              data: {
                'success': true,
                'data': [
                  reminderJson(id: 1, isActive: true),
                  reminderJson(id: 2, isActive: false),
                ],
                'error': null,
              },
              statusCode: 200,
              requestOptions: RequestOptions(path: ''),
            ));

        final result = await service.listReminders(activeOnly: false);

        expect(result, hasLength(2));
        verify(() => mockDio.get(
              ApiConstants.reminders,
              queryParameters: {'active_only': false},
            )).called(1);
      });
    });

    group('updateReminder', () {
      test('부분 업데이트가 정상 동작한다', () async {
        const update = ReminderUpdate(
          reminderTime: '21:00:00',
          isActive: false,
        );

        when(() => mockDio.patch(
              any(),
              data: any(named: 'data'),
            )).thenAnswer((_) async => Response(
              data: {
                'success': true,
                'data': reminderJson(
                  id: 1,
                  reminderTime: '21:00:00',
                  isActive: false,
                ),
                'error': null,
              },
              statusCode: 200,
              requestOptions: RequestOptions(path: ''),
            ));

        final result = await service.updateReminder(1, update);

        expect(result.reminderTime, '21:00:00');
        expect(result.isActive, false);
        verify(() => mockDio.patch(
              ApiConstants.reminder(1),
              data: update.toJson(),
            )).called(1);
      });
    });

    group('deleteReminder', () {
      test('정상적으로 삭제한다', () async {
        when(() => mockDio.delete(any())).thenAnswer((_) async => Response(
              data: {
                'success': true,
                'data': null,
                'error': null,
              },
              statusCode: 200,
              requestOptions: RequestOptions(path: ''),
            ));

        await service.deleteReminder(1);

        verify(() => mockDio.delete(ApiConstants.reminder(1))).called(1);
      });

      test('API 오류 시 DioException을 throw한다', () async {
        when(() => mockDio.delete(any())).thenThrow(DioException(
              requestOptions: RequestOptions(path: ''),
              type: DioExceptionType.badResponse,
              response: Response(
                statusCode: 500,
                requestOptions: RequestOptions(path: ''),
              ),
            ));

        expect(
          () => service.deleteReminder(1),
          throwsA(isA<DioException>()),
        );
      });
    });
  });
}
