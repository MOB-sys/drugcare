import 'package:dio/dio.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';
import 'package:pillright/core/constants/api_constants.dart';
import 'package:pillright/features/result/models/interaction_item.dart';
import 'package:pillright/shared/models/item_type.dart';
import 'package:pillright/shared/services/interaction_service.dart';

class MockDio extends Mock implements Dio {}

void main() {
  late MockDio mockDio;
  late InteractionService service;

  setUp(() {
    mockDio = MockDio();
    service = InteractionService(mockDio);
  });

  group('InteractionService', () {
    group('checkInteractions', () {
      final testItems = [
        const InteractionItem(itemType: ItemType.drug, itemId: 1),
        const InteractionItem(itemType: ItemType.supplement, itemId: 2),
      ];

      test('정상 응답 시 InteractionCheckResponse를 반환한다', () async {
        when(() => mockDio.post(
              any(),
              data: any(named: 'data'),
            )).thenAnswer((_) async => Response(
              data: {
                'success': true,
                'data': {
                  'total_checked': 1,
                  'interactions_found': 1,
                  'has_danger': false,
                  'results': [
                    {
                      'item_a_name': '타이레놀',
                      'item_b_name': '비타민C',
                      'severity': 'info',
                      'description': '특별한 상호작용 없음',
                    },
                  ],
                  'disclaimer': '의사/약사의 전문적 판단을 대체하지 않습니다',
                },
                'error': null,
              },
              statusCode: 200,
              requestOptions: RequestOptions(path: ''),
            ));

        final result = await service.checkInteractions(testItems);

        expect(result.totalChecked, 1);
        expect(result.interactionsFound, 1);
        expect(result.hasDanger, false);
        expect(result.results, hasLength(1));
        expect(result.results.first.itemAName, '타이레놀');
        expect(result.disclaimer, contains('대체하지 않습니다'));
        verify(() => mockDio.post(
              ApiConstants.interactionCheck,
              data: {
                'items': [
                  {'item_type': 'drug', 'item_id': 1},
                  {'item_type': 'supplement', 'item_id': 2},
                ],
              },
            )).called(1);
      });

      test('상호작용이 없을 때 빈 결과를 반환한다', () async {
        when(() => mockDio.post(
              any(),
              data: any(named: 'data'),
            )).thenAnswer((_) async => Response(
              data: {
                'success': true,
                'data': {
                  'total_checked': 1,
                  'interactions_found': 0,
                  'has_danger': false,
                  'results': <dynamic>[],
                  'disclaimer': '의사/약사의 전문적 판단을 대체하지 않습니다',
                },
                'error': null,
              },
              statusCode: 200,
              requestOptions: RequestOptions(path: ''),
            ));

        final result = await service.checkInteractions(testItems);

        expect(result.interactionsFound, 0);
        expect(result.results, isEmpty);
      });

      test('API 오류 시 DioException을 throw한다', () async {
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
          () => service.checkInteractions(testItems),
          throwsA(isA<DioException>()),
        );
      });
    });
  });
}
