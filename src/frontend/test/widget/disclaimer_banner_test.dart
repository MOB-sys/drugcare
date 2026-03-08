import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:pillright/core/constants/app_constants.dart';
import 'package:pillright/shared/widgets/common/disclaimer_banner.dart';

void main() {
  group('DisclaimerBanner', () {
    testWidgets('renders warning icon', (tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(body: DisclaimerBanner()),
        ),
      );

      expect(find.byIcon(Icons.warning_amber_rounded), findsOneWidget);
    });

    testWidgets('displays disclaimer text from AppConstants.disclaimer',
        (tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(body: DisclaimerBanner()),
        ),
      );

      expect(find.text(AppConstants.disclaimer), findsOneWidget);
    });

    testWidgets('has amber/yellow background color', (tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(body: DisclaimerBanner()),
        ),
      );

      final container = tester.widget<Container>(
        find.descendant(
          of: find.byType(DisclaimerBanner),
          matching: find.byType(Container),
        ),
      );

      final decoration = container.decoration as BoxDecoration;
      expect(decoration.color, const Color(0xFFFFF8E1));
    });

    testWidgets('shows chevron icon when onTap is provided', (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(body: DisclaimerBanner(onTap: () {})),
        ),
      );

      expect(find.byIcon(Icons.chevron_right), findsOneWidget);
    });

    testWidgets('hides chevron icon when onTap is null', (tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(body: DisclaimerBanner()),
        ),
      );

      expect(find.byIcon(Icons.chevron_right), findsNothing);
    });

    testWidgets('calls onTap when tapped', (tester) async {
      var tapped = false;
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: DisclaimerBanner(onTap: () => tapped = true),
          ),
        ),
      );

      await tester.tap(find.byType(DisclaimerBanner));
      expect(tapped, isTrue);
    });
  });
}
