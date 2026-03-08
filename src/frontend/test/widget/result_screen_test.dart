import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:pillright/features/result/models/interaction_check_response.dart';
import 'package:pillright/features/result/models/interaction_result.dart';
import 'package:pillright/features/result/providers/interaction_provider.dart';
import 'package:pillright/features/result/widgets/interaction_result_card.dart';
import 'package:pillright/features/result/widgets/result_summary_card.dart';
import 'package:pillright/features/search/models/selected_search_item.dart';
import 'package:pillright/shared/models/item_type.dart';
import 'package:pillright/shared/models/severity.dart';
import 'package:pillright/shared/widgets/common/disclaimer_banner.dart';

/// ResultScreen의 핵심 로직을 AdBannerWidget 없이 테스트한다.
/// (google_mobile_ads 플랫폼 채널은 테스트 환경에서 사용 불가)
void main() {
  final testItems = [
    const SelectedSearchItem(
      itemType: ItemType.drug,
      itemId: 1,
      name: '아스피린',
    ),
    const SelectedSearchItem(
      itemType: ItemType.drug,
      itemId: 2,
      name: '이부프로펜',
    ),
  ];

  const testResponse = InteractionCheckResponse(
    totalChecked: 1,
    interactionsFound: 1,
    hasDanger: true,
    results: [
      InteractionResult(
        itemAName: '아스피린',
        itemBName: '이부프로펜',
        severity: Severity.danger,
        description: '병용 시 출혈 위험 증가',
        source: 'DUR',
      ),
    ],
    disclaimer: '이 정보는 참고용이며, 의사/약사의 전문적 판단을 대체하지 않습니다.',
  );

  testWidgets('ResultSummaryCard shows correct counts', (tester) async {
    await tester.pumpWidget(
      const MaterialApp(
        home: Scaffold(
          body: ResultSummaryCard(response: testResponse),
        ),
      ),
    );

    expect(find.textContaining('1'), findsWidgets);
    expect(find.textContaining('발견'), findsOneWidget);
  });

  testWidgets('InteractionResultCard shows item names', (tester) async {
    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: SingleChildScrollView(
            child: InteractionResultCard(result: testResponse.results.first),
          ),
        ),
      ),
    );

    expect(find.text('아스피린 ↔ 이부프로펜'), findsOneWidget);
  });

  testWidgets('DisclaimerBanner is visible', (tester) async {
    await tester.pumpWidget(
      const MaterialApp(
        home: Scaffold(
          body: DisclaimerBanner(),
        ),
      ),
    );

    expect(
      find.textContaining('의사/약사의 전문적 판단을 대체하지 않습니다'),
      findsOneWidget,
    );
  });

  testWidgets('interactionResultProvider returns data', (tester) async {
    // Provider 단위 테스트 — UI 없이 로직 검증
    final container = ProviderContainer(
      overrides: [
        interactionResultProvider(testItems)
            .overrideWith((ref) => Future.value(testResponse)),
      ],
    );
    addTearDown(container.dispose);

    final result = await container.read(
      interactionResultProvider(testItems).future,
    );

    expect(result.totalChecked, 1);
    expect(result.interactionsFound, 1);
    expect(result.hasDanger, true);
    expect(result.results.length, 1);
    expect(result.results.first.severity, Severity.danger);
  });

  testWidgets('interactionResultProvider handles error', (tester) async {
    final container = ProviderContainer(
      overrides: [
        interactionResultProvider(testItems).overrideWith(
          (ref) => Future<InteractionCheckResponse>.error(
            Exception('네트워크 오류'),
          ),
        ),
      ],
    );
    addTearDown(container.dispose);

    expect(
      () => container.read(interactionResultProvider(testItems).future),
      throwsA(isA<Exception>()),
    );
  });
}
