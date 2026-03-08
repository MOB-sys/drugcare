import 'package:flutter_test/flutter_test.dart';
import 'package:pillright/features/cabinet/models/cabinet_item.dart';
import 'package:pillright/shared/models/item_type.dart';

void main() {
  group('CabinetItem', () {
    test('fromJson creates correct object', () {
      final json = {
        'id': 1,
        'device_id': 'test-device-123',
        'item_type': 'drug',
        'item_id': 42,
        'item_name': '타이레놀',
        'nickname': '두통약',
        'created_at': '2026-01-15T09:30:00',
      };

      final item = CabinetItem.fromJson(json);

      expect(item.id, 1);
      expect(item.deviceId, 'test-device-123');
      expect(item.itemType, ItemType.drug);
      expect(item.itemId, 42);
      expect(item.itemName, '타이레놀');
      expect(item.nickname, '두통약');
      expect(item.createdAt, DateTime(2026, 1, 15, 9, 30));
    });

    test('fromJson handles null nickname', () {
      final json = {
        'id': 2,
        'device_id': 'test-device-456',
        'item_type': 'supplement',
        'item_id': 10,
        'item_name': '비타민D',
        'nickname': null,
        'created_at': '2026-02-01T12:00:00',
      };

      final item = CabinetItem.fromJson(json);

      expect(item.nickname, isNull);
      expect(item.itemType, ItemType.supplement);
      expect(item.itemName, '비타민D');
    });

    test('fromJson parses supplement item type', () {
      final json = {
        'id': 3,
        'device_id': 'dev-789',
        'item_type': 'supplement',
        'item_id': 5,
        'item_name': '오메가3',
        'created_at': '2026-01-20T15:00:00',
      };

      final item = CabinetItem.fromJson(json);
      expect(item.itemType, ItemType.supplement);
    });
  });

  group('CabinetItemCreate', () {
    test('toJson serializes correctly', () {
      const create = CabinetItemCreate(
        itemType: ItemType.drug,
        itemId: 42,
        nickname: '두통약',
      );

      final json = create.toJson();

      expect(json['item_type'], 'drug');
      expect(json['item_id'], 42);
      expect(json['nickname'], '두통약');
    });

    test('toJson includes null nickname', () {
      const create = CabinetItemCreate(
        itemType: ItemType.supplement,
        itemId: 10,
      );

      final json = create.toJson();

      expect(json['item_type'], 'supplement');
      expect(json['item_id'], 10);
      expect(json['nickname'], isNull);
      expect(json.containsKey('nickname'), isTrue);
    });
  });
}
