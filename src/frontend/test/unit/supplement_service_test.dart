import 'package:dio/dio.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';
import 'package:pillright/core/constants/api_constants.dart';
import 'package:pillright/shared/services/supplement_service.dart';

class MockDio extends Mock implements Dio {}

void main() {
  late MockDio mockDio;
  late SupplementService service;

  setUp(() {
    mockDio = MockDio();
    service = SupplementService(mockDio);
  });

  group('SupplementService', () {
    group('searchSupplements', () {
      test('정상 응답 시 PaginatedResult를 반환한다', () async {
        when(() => mockDio.get(
              any(),
              queryParameters: any(named: 'queryParameters'),
            )).thenAnswer((_) async => Response(
              data: {
                'success': true,
                'data': {
                  'items': [
                    {
                      'id': 1,
                      'product_name': '종근당 비타민C 1000',
                      'company': '종근당',
                      'main_ingredient': '비타민C',
                      'category': '비타민',
                    },
                  ],
                  'total': 1,
                  'page': 1,
                  'page_size': 20,
                  'total_pages': 1,
                },
                'error': null,
                'meta': {'timestamp': '2026-01-15T09:30:00Z'},
              },
              statusCode: 200,
              requestOptions: RequestOptions(path: ''),
            ));

        final result = await service.searchSupplements('비타민');

        expect(result.items, hasLength(1));
        expect(result.items.first.productName, '종근당 비타민C 1000');
        expect(result.items.first.company, '종근당');
        expect(result.total, 1);
        verify(() => mockDio.get(
              ApiConstants.supplementSearch,
              queryParameters: {
                'query': '비타민',
                'page': 1,
                'page_size': 20,
              },
            )).called(1);
      });

      test('빈 결과를 올바르게 처리한다', () async {
        when(() => mockDio.get(
              any(),
              queryParameters: any(named: 'queryParameters'),
            )).thenAnswer((_) async => Response(
              data: {
                'success': true,
                'data': {
                  'items': <dynamic>[],
                  'total': 0,
                  'page': 1,
                  'page_size': 20,
                  'total_pages': 0,
                },
                'error': null,
              },
              statusCode: 200,
              requestOptions: RequestOptions(path: ''),
            ));

        final result = await service.searchSupplements('없는영양제');

        expect(result.items, isEmpty);
        expect(result.total, 0);
      });

      test('API 오류 시 DioException을 throw한다', () async {
        when(() => mockDio.get(
              any(),
              queryParameters: any(named: 'queryParameters'),
            )).thenThrow(DioException(
              requestOptions: RequestOptions(path: ''),
              type: DioExceptionType.badResponse,
              response: Response(
                statusCode: 500,
                requestOptions: RequestOptions(path: ''),
              ),
            ));

        expect(
          () => service.searchSupplements('비타민'),
          throwsA(isA<DioException>()),
        );
      });
    });

    group('getSupplementDetail', () {
      test('정상 응답 시 SupplementDetail을 반환한다', () async {
        when(() => mockDio.get(any())).thenAnswer((_) async => Response(
              data: {
                'success': true,
                'data': {
                  'id': 1,
                  'product_name': '종근당 비타민C 1000',
                  'company': '종근당',
                  'registration_no': '20200001',
                  'main_ingredient': '비타민C',
                  'functionality': '항산화 작용',
                  'precautions': '과량 섭취 주의',
                  'intake_method': '1일 1회, 1회 1정',
                  'category': '비타민',
                  'source': '식약처',
                },
                'error': null,
              },
              statusCode: 200,
              requestOptions: RequestOptions(path: ''),
            ));

        final result = await service.getSupplementDetail(1);

        expect(result.id, 1);
        expect(result.productName, '종근당 비타민C 1000');
        expect(result.functionality, '항산화 작용');
        verify(() => mockDio.get(ApiConstants.supplementDetail(1))).called(1);
      });

      test('404 오류 시 DioException을 throw한다', () async {
        when(() => mockDio.get(any())).thenThrow(DioException(
              requestOptions: RequestOptions(path: ''),
              type: DioExceptionType.badResponse,
              response: Response(
                statusCode: 404,
                requestOptions: RequestOptions(path: ''),
              ),
            ));

        expect(
          () => service.getSupplementDetail(99999),
          throwsA(isA<DioException>()),
        );
      });
    });
  });
}
