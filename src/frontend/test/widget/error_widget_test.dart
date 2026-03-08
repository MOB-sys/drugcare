import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:pillright/shared/widgets/common/error_widget.dart';

void main() {
  group('AppErrorWidget', () {
    testWidgets('displays error message', (tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(
            body: AppErrorWidget(message: '네트워크 오류가 발생했습니다.'),
          ),
        ),
      );

      expect(find.text('네트워크 오류가 발생했습니다.'), findsOneWidget);
    });

    testWidgets('shows retry button with text 다시 시도', (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: AppErrorWidget(message: '오류', onRetry: () {}),
          ),
        ),
      );

      expect(find.text('다시 시도'), findsOneWidget);
      expect(find.byType(ElevatedButton), findsOneWidget);
    });

    testWidgets('calls onRetry when retry button tapped', (tester) async {
      var retryCalled = false;
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: AppErrorWidget(
              message: '오류',
              onRetry: () => retryCalled = true,
            ),
          ),
        ),
      );

      await tester.tap(find.text('다시 시도'));
      expect(retryCalled, isTrue);
    });

    testWidgets('hides retry button when onRetry is null', (tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(
            body: AppErrorWidget(message: '오류'),
          ),
        ),
      );

      expect(find.text('다시 시도'), findsNothing);
      expect(find.byType(ElevatedButton), findsNothing);
    });

    testWidgets('shows error_outline icon', (tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(
            body: AppErrorWidget(message: '오류'),
          ),
        ),
      );

      expect(find.byIcon(Icons.error_outline), findsOneWidget);
    });
  });
}
