import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:yakmeogeo/shared/widgets/common/empty_state_widget.dart';

void main() {
  group('EmptyStateWidget', () {
    testWidgets('메시지가 표시된다', (tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(
            body: EmptyStateWidget(message: '검색 결과가 없습니다'),
          ),
        ),
      );

      expect(find.text('검색 결과가 없습니다'), findsOneWidget);
    });

    testWidgets('기본 아이콘이 inbox_outlined이다', (tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(
            body: EmptyStateWidget(message: '비어있음'),
          ),
        ),
      );

      expect(find.byIcon(Icons.inbox_outlined), findsOneWidget);
    });

    testWidgets('커스텀 아이콘이 표시된다', (tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(
            body: EmptyStateWidget(
              message: '알림 없음',
              icon: Icons.notifications_off_outlined,
            ),
          ),
        ),
      );

      expect(find.byIcon(Icons.notifications_off_outlined), findsOneWidget);
      expect(find.byIcon(Icons.inbox_outlined), findsNothing);
    });
  });
}
