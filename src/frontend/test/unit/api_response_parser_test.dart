import 'package:flutter_test/flutter_test.dart';
import 'package:yakmeogeo/core/utils/api_response_parser.dart';

void main() {
  group('ApiResponseParser', () {
    group('parse', () {
      test('extracts data on success', () {
        final json = {
          'success': true,
          'data': {'name': '타이레놀', 'id': 1},
          'error': null,
          'meta': {'timestamp': '2026-01-15T09:30:00Z'},
        };

        final result = ApiResponseParser.parse<Map<String, dynamic>>(
          json,
          (data) => data as Map<String, dynamic>,
        );

        expect(result['name'], '타이레놀');
        expect(result['id'], 1);
      });

      test('throws ApiException on failure', () {
        final json = {
          'success': false,
          'data': null,
          'error': '약물을 찾을 수 없습니다.',
          'meta': {'timestamp': '2026-01-15T09:30:00Z'},
        };

        expect(
          () => ApiResponseParser.parse(json, (data) => data),
          throwsA(isA<ApiException>()),
        );
      });

      test('ApiException contains error message', () {
        final json = {
          'success': false,
          'data': null,
          'error': '서버 오류가 발생했습니다.',
        };

        try {
          ApiResponseParser.parse(json, (data) => data);
          fail('Expected ApiException');
        } on ApiException catch (e) {
          expect(e.message, '서버 오류가 발생했습니다.');
          expect(e.toString(), 'ApiException: 서버 오류가 발생했습니다.');
        }
      });

      test('handles missing error message gracefully', () {
        final json = {
          'success': false,
          'data': null,
        };

        expect(
          () => ApiResponseParser.parse(json, (data) => data),
          throwsA(
            isA<ApiException>().having(
              (e) => e.message,
              'message',
              '알 수 없는 오류가 발생했습니다.',
            ),
          ),
        );
      });

      test('treats missing success field as false', () {
        final json = <String, dynamic>{
          'data': {'id': 1},
        };

        expect(
          () => ApiResponseParser.parse(json, (data) => data),
          throwsA(isA<ApiException>()),
        );
      });
    });

    group('parseList', () {
      test('extracts list data', () {
        final json = {
          'success': true,
          'data': [
            {'id': 1, 'name': '아스피린'},
            {'id': 2, 'name': '타이레놀'},
          ],
          'error': null,
        };

        final result = ApiResponseParser.parseList<Map<String, dynamic>>(
          json,
          (item) => item,
        );

        expect(result, hasLength(2));
        expect(result[0]['name'], '아스피린');
        expect(result[1]['name'], '타이레놀');
      });

      test('returns empty list when data is empty', () {
        final json = {
          'success': true,
          'data': <dynamic>[],
          'error': null,
        };

        final result = ApiResponseParser.parseList<Map<String, dynamic>>(
          json,
          (item) => item,
        );

        expect(result, isEmpty);
      });

      test('throws ApiException on failure', () {
        final json = {
          'success': false,
          'data': null,
          'error': '목록 조회 실패',
        };

        expect(
          () => ApiResponseParser.parseList(json, (item) => item),
          throwsA(isA<ApiException>()),
        );
      });
    });
  });
}
