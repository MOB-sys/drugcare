import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:pillright/features/search/screens/search_screen.dart';

void main() {
  Widget buildWidget() {
    return const ProviderScope(
      child: MaterialApp(
        home: SearchScreen(),
      ),
    );
  }

  testWidgets('앱바에 "약/영양제 검색"을 표시한다', (tester) async {
    await tester.pumpWidget(buildWidget());

    expect(find.text('약/영양제 검색'), findsOneWidget);
  });

  testWidgets('검색 텍스트 필드를 표시한다', (tester) async {
    await tester.pumpWidget(buildWidget());

    expect(find.byType(TextField), findsOneWidget);
  });

  testWidgets('필터 칩 3개를 표시한다 (전체, 약물, 영양제)', (tester) async {
    await tester.pumpWidget(buildWidget());

    expect(find.text('전체'), findsOneWidget);
    expect(find.text('약물'), findsOneWidget);
    expect(find.text('영양제'), findsOneWidget);
  });

  testWidgets('초기 빈 상태 메시지를 표시한다', (tester) async {
    await tester.pumpWidget(buildWidget());

    expect(
      find.textContaining('상호작용을 확인해 보세요'),
      findsOneWidget,
    );
  });
}
