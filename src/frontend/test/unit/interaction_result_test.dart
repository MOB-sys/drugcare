import 'package:flutter_test/flutter_test.dart';
import 'package:pillright/features/result/models/interaction_result.dart';
import 'package:pillright/shared/models/severity.dart';

void main() {
  group('InteractionResult', () {
    test('fromJson creates correct object with all fields', () {
      final json = {
        'item_a_name': '아스피린',
        'item_b_name': '와파린',
        'severity': 'danger',
        'description': '출혈 위험 증가',
        'mechanism': '항혈소판 + 항응고 효과 중복',
        'recommendation': '병용 금기. 의사와 상의하세요.',
        'source': 'DUR',
        'evidence_level': 'high',
      };

      final result = InteractionResult.fromJson(json);

      expect(result.itemAName, '아스피린');
      expect(result.itemBName, '와파린');
      expect(result.severity, Severity.danger);
      expect(result.description, '출혈 위험 증가');
      expect(result.mechanism, '항혈소판 + 항응고 효과 중복');
      expect(result.recommendation, '병용 금기. 의사와 상의하세요.');
      expect(result.source, 'DUR');
      expect(result.evidenceLevel, 'high');
    });

    test('fromJson handles null optional fields', () {
      final json = {
        'item_a_name': '비타민C',
        'item_b_name': '철분제',
        'severity': 'info',
      };

      final result = InteractionResult.fromJson(json);

      expect(result.itemAName, '비타민C');
      expect(result.itemBName, '철분제');
      expect(result.severity, Severity.info);
      expect(result.description, isNull);
      expect(result.mechanism, isNull);
      expect(result.recommendation, isNull);
      expect(result.source, isNull);
      expect(result.evidenceLevel, isNull);
    });

    test('severity is correctly parsed for each level', () {
      for (final severity in Severity.values) {
        final json = {
          'item_a_name': 'A',
          'item_b_name': 'B',
          'severity': severity.name,
        };

        final result = InteractionResult.fromJson(json);
        expect(result.severity, severity);
      }
    });

    test('fromJson throws on unknown severity', () {
      final json = {
        'item_a_name': 'A',
        'item_b_name': 'B',
        'severity': 'unknown',
      };

      expect(
        () => InteractionResult.fromJson(json),
        throwsA(isA<ArgumentError>()),
      );
    });
  });
}
