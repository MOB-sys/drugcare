import 'package:dio/dio.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';
import 'package:yakmeogeo/core/constants/api_constants.dart';
import 'package:yakmeogeo/features/cabinet/models/cabinet_item.dart';
import 'package:yakmeogeo/shared/models/item_type.dart';
import 'package:yakmeogeo/shared/services/cabinet_service.dart';

class MockDio extends Mock implements Dio {}

void main() {
  late MockDio mockDio;
  late CabinetService service;

  setUp(() {
    mockDio = MockDio();
    service = CabinetService(mockDio);
  });

  group('CabinetService', () {
    group('addItem', () {
      test('정상 응답 시 CabinetItem을 반환한다', () async {
        const createItem = CabinetItemCreate(
          itemType: ItemType.drug,
          itemId: 1,
          nickname: '아침약',
        );

        when(() => mockDio.post(
              any(),
              data: any(named: 'data'),
            )).thenAnswer((_) async => Response(
              data: {
                'success': true,
                'data': {
                  'id': 10,
                  'device_id': 'test-device-123',
                  'item_type': 'drug',
                  'item_id': 1,
                  'item_name': '타이레놀정500밀리그램',
                  'nickname': '아침약',
                  'created_at': '2026-01-15T09:30:00Z',
                },
                'error': null,
              },
              statusCode: 201,
              requestOptions: RequestOptions(path: ''),
            ));

        final result = await service.addItem(createItem);

        expect(result.id, 10);
        expect(result.itemName, '타이레놀정500밀리그램');
        expect(result.nickname, '아침약');
        expect(result.itemType, ItemType.drug);
        verify(() => mockDio.post(
              ApiConstants.cabinet,
              data: createItem.toJson(),
            )).called(1);
      });

      test('중복 409 오류 시 DioException을 throw한다', () async {
        const createItem = CabinetItemCreate(
          itemType: ItemType.drug,
          itemId: 1,
        );

        when(() => mockDio.post(
              any(),
              data: any(named: 'data'),
            )).thenThrow(DioException(
              requestOptions: RequestOptions(path: ''),
              type: DioExceptionType.badResponse,
              response: Response(
                statusCode: 409,
                data: {
                  'success': false,
                  'error': '이미 복약함에 추가된 아이템입니다.',
                },
                requestOptions: RequestOptions(path: ''),
              ),
            ));

        expect(
          () => service.addItem(createItem),
          throwsA(isA<DioException>()),
        );
      });
    });

    group('listItems', () {
      test('아이템 목록을 반환한다', () async {
        when(() => mockDio.get(any())).thenAnswer((_) async => Response(
              data: {
                'success': true,
                'data': [
                  {
                    'id': 1,
                    'device_id': 'test-device-123',
                    'item_type': 'drug',
                    'item_id': 10,
                    'item_name': '타이레놀정500밀리그램',
                    'nickname': null,
                    'created_at': '2026-01-15T09:30:00Z',
                  },
                  {
                    'id': 2,
                    'device_id': 'test-device-123',
                    'item_type': 'supplement',
                    'item_id': 20,
                    'item_name': '종근당 비타민C 1000',
                    'nickname': '비타민',
                    'created_at': '2026-01-16T10:00:00Z',
                  },
                ],
                'error': null,
              },
              statusCode: 200,
              requestOptions: RequestOptions(path: ''),
            ));

        final result = await service.listItems();

        expect(result, hasLength(2));
        expect(result[0].itemType, ItemType.drug);
        expect(result[1].itemType, ItemType.supplement);
        verify(() => mockDio.get(ApiConstants.cabinet)).called(1);
      });

      test('빈 목록을 반환한다', () async {
        when(() => mockDio.get(any())).thenAnswer((_) async => Response(
              data: {
                'success': true,
                'data': <dynamic>[],
                'error': null,
              },
              statusCode: 200,
              requestOptions: RequestOptions(path: ''),
            ));

        final result = await service.listItems();

        expect(result, isEmpty);
      });
    });

    group('deleteItem', () {
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

        await service.deleteItem(1);

        verify(() => mockDio.delete(ApiConstants.cabinetItem(1))).called(1);
      });

      test('404 오류 시 DioException을 throw한다', () async {
        when(() => mockDio.delete(any())).thenThrow(DioException(
              requestOptions: RequestOptions(path: ''),
              type: DioExceptionType.badResponse,
              response: Response(
                statusCode: 404,
                requestOptions: RequestOptions(path: ''),
              ),
            ));

        expect(
          () => service.deleteItem(99999),
          throwsA(isA<DioException>()),
        );
      });
    });
  });
}
