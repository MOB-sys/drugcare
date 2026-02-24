import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:yakmeogeo/shared/models/item_type.dart';
import 'package:yakmeogeo/shared/widgets/common/search_item_card.dart';

void main() {
  group('SearchItemCard', () {
    testWidgets('약물 아이템은 "약물" 태그와 이름을 표시한다', (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: SearchItemCard(
              name: '타이레놀정500밀리그램',
              itemType: ItemType.drug,
              isSelected: false,
              onTap: () {},
            ),
          ),
        ),
      );

      expect(find.text('약물'), findsOneWidget);
      expect(find.text('타이레놀정500밀리그램'), findsOneWidget);
    });

    testWidgets('영양제 아이템은 "영양제" 태그를 표시한다', (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: SearchItemCard(
              name: '비타민C 1000',
              itemType: ItemType.supplement,
              isSelected: false,
              onTap: () {},
            ),
          ),
        ),
      );

      expect(find.text('영양제'), findsOneWidget);
      expect(find.text('비타민C 1000'), findsOneWidget);
    });

    testWidgets('선택 상태에서 check_circle 아이콘을 표시한다', (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: SearchItemCard(
              name: '타이레놀',
              itemType: ItemType.drug,
              isSelected: true,
              onTap: () {},
            ),
          ),
        ),
      );

      expect(find.byIcon(Icons.check_circle), findsOneWidget);
      expect(find.byIcon(Icons.radio_button_unchecked), findsNothing);
    });

    testWidgets('미선택 상태에서 radio_button_unchecked 아이콘을 표시한다',
        (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: SearchItemCard(
              name: '타이레놀',
              itemType: ItemType.drug,
              isSelected: false,
              onTap: () {},
            ),
          ),
        ),
      );

      expect(find.byIcon(Icons.radio_button_unchecked), findsOneWidget);
      expect(find.byIcon(Icons.check_circle), findsNothing);
    });

    testWidgets('subtitle이 제공되면 표시한다', (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: SearchItemCard(
              name: '타이레놀정500밀리그램',
              subtitle: '한국존슨앤드존슨',
              itemType: ItemType.drug,
              isSelected: false,
              onTap: () {},
            ),
          ),
        ),
      );

      expect(find.text('한국존슨앤드존슨'), findsOneWidget);
    });

    testWidgets('onTap 콜백이 동작한다', (tester) async {
      var tapped = false;

      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: SearchItemCard(
              name: '타이레놀',
              itemType: ItemType.drug,
              isSelected: false,
              onTap: () => tapped = true,
            ),
          ),
        ),
      );

      await tester.tap(find.byType(SearchItemCard));
      expect(tapped, true);
    });
  });
}
