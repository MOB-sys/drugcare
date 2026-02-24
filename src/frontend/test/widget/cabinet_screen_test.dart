import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:yakmeogeo/features/cabinet/models/cabinet_item.dart';
import 'package:yakmeogeo/features/cabinet/providers/cabinet_provider.dart';
import 'package:yakmeogeo/features/cabinet/screens/cabinet_screen.dart';
import 'package:yakmeogeo/shared/models/item_type.dart';

/// 테스트용 CabinetNotifier (서버 호출 없이 제어 가능).
class FakeCabinetNotifier extends StateNotifier<CabinetState>
    implements CabinetNotifier {
  FakeCabinetNotifier(this._items)
      : super(CabinetState(items: AsyncValue.data(_items)));

  final List<CabinetItem> _items;

  @override
  // ignore: no-empty-block
  dynamic noSuchMethod(Invocation invocation) => super.noSuchMethod(invocation);

  @override
  Future<void> loadItems() async {
    state = CabinetState(items: AsyncValue.data(_items));
  }
}

/// 로딩 상태를 유지하는 테스트용 CabinetNotifier.
class LoadingCabinetNotifier extends StateNotifier<CabinetState>
    implements CabinetNotifier {
  LoadingCabinetNotifier() : super(const CabinetState());

  @override
  // ignore: no-empty-block
  dynamic noSuchMethod(Invocation invocation) => super.noSuchMethod(invocation);

  @override
  Future<void> loadItems() async {}
}

void main() {
  Widget buildWidget({List<CabinetItem> items = const []}) {
    return ProviderScope(
      overrides: [
        cabinetProvider.overrideWith(
          (ref) => FakeCabinetNotifier(items),
        ),
      ],
      child: const MaterialApp(
        home: CabinetScreen(),
      ),
    );
  }

  testWidgets('앱바에 "내 복약함"을 표시한다', (tester) async {
    await tester.pumpWidget(buildWidget());
    await tester.pumpAndSettle();

    expect(find.text('내 복약함'), findsOneWidget);
  });

  testWidgets('FAB 추가 버튼을 표시한다', (tester) async {
    await tester.pumpWidget(buildWidget());
    await tester.pumpAndSettle();

    expect(find.byType(FloatingActionButton), findsOneWidget);
    expect(find.byIcon(Icons.add), findsOneWidget);
  });

  testWidgets('로딩 상태를 표시한다', (tester) async {
    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          cabinetProvider.overrideWith(
            (ref) => LoadingCabinetNotifier(),
          ),
        ],
        child: const MaterialApp(
          home: CabinetScreen(),
        ),
      ),
    );

    expect(find.byType(CircularProgressIndicator), findsOneWidget);
    expect(find.text('복약함을 불러오는 중...'), findsOneWidget);
  });

  testWidgets('아이템이 없으면 빈 상태를 표시한다', (tester) async {
    await tester.pumpWidget(buildWidget());
    await tester.pumpAndSettle();

    expect(find.textContaining('복약함이 비어있습니다'), findsOneWidget);
  });

  testWidgets('아이템이 있으면 목록을 표시한다', (tester) async {
    await tester.pumpWidget(
      buildWidget(
        items: [
          CabinetItem(
            id: 1,
            deviceId: 'test',
            itemType: ItemType.drug,
            itemId: 100,
            itemName: '타이레놀',
            nickname: null,
            createdAt: DateTime.now(),
          ),
        ],
      ),
    );
    await tester.pumpAndSettle();

    expect(find.text('타이레놀'), findsOneWidget);
  });
}
