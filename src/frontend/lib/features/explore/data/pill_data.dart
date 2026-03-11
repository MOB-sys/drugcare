/// 알약 색상 정보.
class PillColor {
  /// 표시 라벨.
  final String label;

  /// API 전송 값.
  final String value;

  /// 표시용 색상 코드 (ARGB).
  final int colorCode;

  /// [PillColor] 생성자.
  const PillColor({
    required this.label,
    required this.value,
    required this.colorCode,
  });
}

/// 알약 색상 목록.
const List<PillColor> pillColors = [
  PillColor(label: '하양', value: '하양', colorCode: 0xFFFFFFFF),
  PillColor(label: '노랑', value: '노랑', colorCode: 0xFFFFEB3B),
  PillColor(label: '주황', value: '주황', colorCode: 0xFFFF9800),
  PillColor(label: '분홍', value: '분홍', colorCode: 0xFFE91E63),
  PillColor(label: '빨강', value: '빨강', colorCode: 0xFFF44336),
  PillColor(label: '갈색', value: '갈색', colorCode: 0xFF795548),
  PillColor(label: '연두', value: '연두', colorCode: 0xFF8BC34A),
  PillColor(label: '초록', value: '초록', colorCode: 0xFF4CAF50),
  PillColor(label: '청록', value: '청록', colorCode: 0xFF009688),
  PillColor(label: '파랑', value: '파랑', colorCode: 0xFF2196F3),
  PillColor(label: '남색', value: '남색', colorCode: 0xFF3F51B5),
  PillColor(label: '보라', value: '보라', colorCode: 0xFF9C27B0),
  PillColor(label: '회색', value: '회색', colorCode: 0xFF9E9E9E),
  PillColor(label: '검정', value: '검정', colorCode: 0xFF212121),
  PillColor(label: '투명', value: '투명', colorCode: 0x00000000),
];

/// 알약 모양 정보.
class PillShape {
  /// 표시 라벨.
  final String label;

  /// API 전송 값.
  final String value;

  /// 표시용 아이콘 문자.
  final String icon;

  /// [PillShape] 생성자.
  const PillShape({
    required this.label,
    required this.value,
    required this.icon,
  });
}

/// 알약 모양 목록.
const List<PillShape> pillShapes = [
  PillShape(label: '원형', value: '원형', icon: '●'),
  PillShape(label: '타원형', value: '타원형', icon: '⬮'),
  PillShape(label: '장방형', value: '장방형', icon: '▬'),
  PillShape(label: '삼각형', value: '삼각형', icon: '▲'),
  PillShape(label: '사각형', value: '사각형', icon: '■'),
  PillShape(label: '마름모형', value: '마름모형', icon: '◆'),
  PillShape(label: '오각형', value: '오각형', icon: '⬠'),
  PillShape(label: '육각형', value: '육각형', icon: '⬡'),
  PillShape(label: '팔각형', value: '팔각형', icon: '⯃'),
  PillShape(label: '반원형', value: '반원형', icon: '◗'),
  PillShape(label: '기타', value: '기타', icon: '?'),
];
