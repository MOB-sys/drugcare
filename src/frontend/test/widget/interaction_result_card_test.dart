import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:yakmeogeo/features/result/models/interaction_result.dart';
import 'package:yakmeogeo/features/result/widgets/interaction_result_card.dart';
import 'package:yakmeogeo/shared/models/severity.dart';

void main() {
  const testResult = InteractionResult(
    itemAName: '아스피린',
    itemBName: '이부프로펜',
    severity: Severity.danger,
    description: '병용 시 출혈 위험 증가',
    mechanism: 'COX 억제 중복',
    recommendation: '병용 금기',
    source: 'DUR',
    evidenceLevel: 'A',
  );

  Widget buildWidget(InteractionResult result) {
    return MaterialApp(
      home: Scaffold(
        body: SingleChildScrollView(
          child: InteractionResultCard(result: result),
        ),
      ),
    );
  }

  testWidgets('아이템 A, B 이름을 표시한다', (tester) async {
    await tester.pumpWidget(buildWidget(testResult));

    expect(find.text('아스피린 ↔ 이부프로펜'), findsOneWidget);
  });

  testWidgets('심각도 배지 라벨을 표시한다', (tester) async {
    await tester.pumpWidget(buildWidget(testResult));

    expect(find.text('위험'), findsOneWidget);
  });

  testWidgets('설명 텍스트를 표시한다', (tester) async {
    await tester.pumpWidget(buildWidget(testResult));

    expect(find.text('병용 시 출혈 위험 증가'), findsOneWidget);
  });

  testWidgets('탭하면 상세 영역이 확장된다', (tester) async {
    await tester.pumpWidget(buildWidget(testResult));

    // 초기엔 상세 보기 텍스트 있음
    expect(find.text('상세 보기'), findsOneWidget);
    expect(find.text('작용 기전'), findsNothing);

    // 탭하면 확장
    await tester.tap(find.text('상세 보기'));
    await tester.pumpAndSettle();

    expect(find.text('작용 기전'), findsOneWidget);
    expect(find.text('COX 억제 중복'), findsOneWidget);
    expect(find.text('권장 사항'), findsOneWidget);
    expect(find.text('병용 금기'), findsOneWidget);
    expect(find.text('출처'), findsOneWidget);
    expect(find.text('DUR'), findsOneWidget);
    expect(find.text('근거 수준'), findsOneWidget);
    expect(find.text('A'), findsOneWidget);
    expect(find.text('접기'), findsOneWidget);
  });

  testWidgets('각 심각도에 맞는 배지를 표시한다', (tester) async {
    for (final severity in Severity.values) {
      final result = InteractionResult(
        itemAName: 'A',
        itemBName: 'B',
        severity: severity,
        description: '설명',
      );

      await tester.pumpWidget(buildWidget(result));
      expect(find.text(severity.label), findsOneWidget);
    }
  });

  testWidgets('심각도에 맞는 배경색을 사용한다', (tester) async {
    for (final severity in Severity.values) {
      final result = InteractionResult(
        itemAName: 'A',
        itemBName: 'B',
        severity: severity,
        description: '설명',
      );

      await tester.pumpWidget(buildWidget(result));

      final containerFinder = find.byWidgetPredicate((widget) {
        if (widget is Container) {
          final deco = widget.decoration;
          if (deco is BoxDecoration) {
            return deco.color == severity.backgroundColor;
          }
        }
        return false;
      });
      expect(containerFinder, findsAtLeastNWidgets(1),
          reason: '${severity.name}의 배경색이 올바르지 않음');
    }
  });

  testWidgets('AI 설명이 있으면 확장 시 AI 섹션을 표시한다', (tester) async {
    const resultWithAi = InteractionResult(
      itemAName: '아스피린',
      itemBName: '이부프로펜',
      severity: Severity.danger,
      description: '병용 시 출혈 위험 증가',
      source: 'DUR',
      aiExplanation: '이 두 약은 같은 계열의 진통제입니다.',
      aiRecommendation: '복용 간격을 두세요.',
    );

    await tester.pumpWidget(buildWidget(resultWithAi));

    // 초기엔 AI 섹션 안 보임
    expect(find.text('AI 쉬운 설명'), findsNothing);

    // 탭하면 확장
    await tester.tap(find.text('상세 보기'));
    await tester.pumpAndSettle();

    expect(find.text('AI 쉬운 설명'), findsOneWidget);
    expect(find.text('이 두 약은 같은 계열의 진통제입니다.'), findsOneWidget);
    expect(find.text('AI 대처 방법'), findsOneWidget);
    expect(find.text('복용 간격을 두세요.'), findsOneWidget);
  });

  testWidgets('AI 설명이 없으면 AI 섹션을 표시하지 않는다', (tester) async {
    const resultWithoutAi = InteractionResult(
      itemAName: '아스피린',
      itemBName: '이부프로펜',
      severity: Severity.warning,
      description: '주의 필요',
      source: 'DUR',
    );

    await tester.pumpWidget(buildWidget(resultWithoutAi));

    await tester.tap(find.text('상세 보기'));
    await tester.pumpAndSettle();

    expect(find.text('AI 쉬운 설명'), findsNothing);
    expect(find.text('AI 대처 방법'), findsNothing);
  });

  testWidgets('AI 설명만 있고 대처 방법이 없으면 설명만 표시한다', (tester) async {
    const resultAiOnly = InteractionResult(
      itemAName: '아스피린',
      itemBName: '이부프로펜',
      severity: Severity.caution,
      description: '가벼운 상호작용',
      source: 'DUR',
      aiExplanation: 'AI 생성 설명 텍스트입니다.',
    );

    await tester.pumpWidget(buildWidget(resultAiOnly));

    await tester.tap(find.text('상세 보기'));
    await tester.pumpAndSettle();

    expect(find.text('AI 쉬운 설명'), findsOneWidget);
    expect(find.text('AI 생성 설명 텍스트입니다.'), findsOneWidget);
    expect(find.text('AI 대처 방법'), findsNothing);
  });
}
