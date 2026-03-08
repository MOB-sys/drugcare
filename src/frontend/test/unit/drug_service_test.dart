import 'package:dio/dio.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';
import 'package:pillright/core/constants/api_constants.dart';
import 'package:pillright/shared/services/drug_service.dart';

class MockDio extends Mock implements Dio {}

void main() {
  late MockDio mockDio;
  late DrugService service;

  setUp(() {
    mockDio = MockDio();
    service = DrugService(mockDio);
  });

  group('DrugService', () {
    group('searchDrugs', () {
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
                      'item_seq': '200000001',
                      'item_name': '타이레놀정500밀리그램',
                      'entp_name': '한국존슨앤드존슨',
                      'etc_otc_code': '일반',
                      'class_no': '01140',
                      'item_image': null,
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

        final result = await service.searchDrugs('타이레놀');

        expect(result.items, hasLength(1));
        expect(result.items.first.itemName, '타이레놀정500밀리그램');
        expect(result.total, 1);
        expect(result.page, 1);
        verify(() => mockDio.get(
              ApiConstants.drugSearch,
              queryParameters: {'query': '타이레놀', 'page': 1, 'page_size': 20},
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

        final result = await service.searchDrugs('없는약');

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
          () => service.searchDrugs('타이레놀'),
          throwsA(isA<DioException>()),
        );
      });
    });

    group('getDrugDetail', () {
      test('정상 응답 시 DrugDetail을 반환한다', () async {
        when(() => mockDio.get(any())).thenAnswer((_) async => Response(
              data: {
                'success': true,
                'data': {
                  'id': 1,
                  'item_seq': '200000001',
                  'item_name': '타이레놀정500밀리그램',
                  'entp_name': '한국존슨앤드존슨',
                  'etc_otc_code': '일반',
                  'class_no': '01140',
                  'efcy_qesitm': '두통, 치통, 생리통',
                },
                'error': null,
              },
              statusCode: 200,
              requestOptions: RequestOptions(path: ''),
            ));

        final result = await service.getDrugDetail(1);

        expect(result.id, 1);
        expect(result.itemName, '타이레놀정500밀리그램');
        expect(result.efcyQesitm, '두통, 치통, 생리통');
        verify(() => mockDio.get(ApiConstants.drugDetail(1))).called(1);
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
          () => service.getDrugDetail(99999),
          throwsA(isA<DioException>()),
        );
      });
    });
  });
}
