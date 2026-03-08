import 'package:dio/dio.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';
import 'package:pillright/core/constants/api_constants.dart';
import 'package:pillright/shared/services/feedback_service.dart';

class MockDio extends Mock implements Dio {}

void main() {
  late MockDio mockDio;
  late FeedbackService service;

  setUp(() {
    mockDio = MockDio();
    service = FeedbackService(mockDio);
  });

  group('FeedbackService', () {
    group('submit', () {
      test('정상 응답 시 피드백 결과를 반환한다', () async {
        when(() => mockDio.post(
              any(),
              data: any(named: 'data'),
            )).thenAnswer((_) async => Response(
              data: {
                'success': true,
                'data': {
                  'id': 1,
                  'category': 'bug',
                  'content': '검색이 작동하지 않습니다.',
                  'app_version': '1.0.0',
                  'created_at': '2026-02-24T09:00:00Z',
                },
                'error': null,
              },
              statusCode: 200,
              requestOptions: RequestOptions(path: ''),
            ));

        final result = await service.submit(
          category: 'bug',
          content: '검색이 작동하지 않습니다.',
          appVersion: '1.0.0',
          osInfo: 'iOS 17.0',
        );

        expect(result['id'], 1);
        expect(result['category'], 'bug');
        verify(() => mockDio.post(
              ApiConstants.feedback,
              data: {
                'category': 'bug',
                'content': '검색이 작동하지 않습니다.',
                'app_version': '1.0.0',
                'os_info': 'iOS 17.0',
              },
            )).called(1);
      });

      test('기능 제안 피드백을 제출한다', () async {
        when(() => mockDio.post(
              any(),
              data: any(named: 'data'),
            )).thenAnswer((_) async => Response(
              data: {
                'success': true,
                'data': {
                  'id': 2,
                  'category': 'feature',
                  'content': '다크 모드를 추가해주세요.',
                  'app_version': '1.0.0',
                  'created_at': '2026-02-24T10:00:00Z',
                },
                'error': null,
              },
              statusCode: 200,
              requestOptions: RequestOptions(path: ''),
            ));

        final result = await service.submit(
          category: 'feature',
          content: '다크 모드를 추가해주세요.',
        );

        expect(result['category'], 'feature');
      });

      test('서버 오류 시 DioException을 throw한다', () async {
        when(() => mockDio.post(
              any(),
              data: any(named: 'data'),
            )).thenThrow(DioException(
              requestOptions: RequestOptions(path: ''),
              type: DioExceptionType.badResponse,
              response: Response(
                statusCode: 500,
                requestOptions: RequestOptions(path: ''),
              ),
            ));

        expect(
          () => service.submit(
            category: 'bug',
            content: '서버 에러 테스트',
          ),
          throwsA(isA<DioException>()),
        );
      });
    });
  });
}
