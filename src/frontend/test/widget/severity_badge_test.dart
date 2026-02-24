import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:yakmeogeo/shared/models/severity.dart';
import 'package:yakmeogeo/shared/widgets/common/severity_badge.dart';

void main() {
  group('SeverityBadge', () {
    Widget buildBadge(Severity severity) {
      return MaterialApp(
        home: Scaffold(body: SeverityBadge(severity: severity)),
      );
    }

    testWidgets('renders 위험 label for Severity.danger', (tester) async {
      await tester.pumpWidget(buildBadge(Severity.danger));
      expect(find.text('위험'), findsOneWidget);
    });

    testWidgets('renders 경고 label for Severity.warning', (tester) async {
      await tester.pumpWidget(buildBadge(Severity.warning));
      expect(find.text('경고'), findsOneWidget);
    });

    testWidgets('renders 주의 label for Severity.caution', (tester) async {
      await tester.pumpWidget(buildBadge(Severity.caution));
      expect(find.text('주의'), findsOneWidget);
    });

    testWidgets('renders 참고 label for Severity.info', (tester) async {
      await tester.pumpWidget(buildBadge(Severity.info));
      expect(find.text('참고'), findsOneWidget);
    });

    testWidgets('displays dangerous icon for Severity.danger', (tester) async {
      await tester.pumpWidget(buildBadge(Severity.danger));
      expect(find.byIcon(Icons.dangerous), findsOneWidget);
    });

    testWidgets('displays warning icon for Severity.warning', (tester) async {
      await tester.pumpWidget(buildBadge(Severity.warning));
      expect(find.byIcon(Icons.warning), findsOneWidget);
    });

    testWidgets('displays info_outline icon for Severity.caution',
        (tester) async {
      await tester.pumpWidget(buildBadge(Severity.caution));
      expect(find.byIcon(Icons.info_outline), findsOneWidget);
    });

    testWidgets('displays lightbulb_outline icon for Severity.info',
        (tester) async {
      await tester.pumpWidget(buildBadge(Severity.info));
      expect(find.byIcon(Icons.lightbulb_outline), findsOneWidget);
    });
  });
}
