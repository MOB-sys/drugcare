import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:pillright/shared/widgets/common/loading_widget.dart';

void main() {
  group('LoadingWidget', () {
    testWidgets('CircularProgressIndicator가 렌더링된다', (tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(
            body: LoadingWidget(),
          ),
        ),
      );

      expect(find.byType(CircularProgressIndicator), findsOneWidget);
    });

    testWidgets('메시지 없이 생성 시 텍스트가 표시되지 않는다', (tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(
            body: LoadingWidget(),
          ),
        ),
      );

      expect(find.byType(CircularProgressIndicator), findsOneWidget);
      // Text 위젯이 없어야 한다 (CircularProgressIndicator 내부 제외)
      expect(find.byType(Text), findsNothing);
    });

    testWidgets('메시지가 있으면 텍스트가 표시된다', (tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(
            body: LoadingWidget(message: '약물 정보를 불러오는 중...'),
          ),
        ),
      );

      expect(find.byType(CircularProgressIndicator), findsOneWidget);
      expect(find.text('약물 정보를 불러오는 중...'), findsOneWidget);
    });
  });
}
