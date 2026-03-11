/// 자주 찾는 증상 목록.
const List<String> commonSymptoms = [
  '두통',
  '소화불량',
  '감기',
  '생리통',
  '근육통',
  '불면',
  '피로',
  '변비',
  '알레르기',
  '기침',
];

/// 자주 찾는 부작용 목록.
const List<String> commonSideEffects = [
  '졸음',
  '어지러움',
  '구역질',
  '발진',
  '설사',
  '두통',
  '구갈',
  '변비',
  '식욕부진',
  '복통',
];

/// 질환 카테고리.
class ConditionCategory {
  /// 카테고리 라벨.
  final String label;

  /// 검색 키워드.
  final String keyword;

  /// 설명 텍스트.
  final String description;

  /// [ConditionCategory] 생성자.
  const ConditionCategory({
    required this.label,
    required this.keyword,
    required this.description,
  });
}

/// 질환 카테고리 목록.
const List<ConditionCategory> conditionCategories = [
  ConditionCategory(
    label: '임산부',
    keyword: '임부',
    description: '임신 중 주의 약물',
  ),
  ConditionCategory(
    label: '고혈압',
    keyword: '고혈압',
    description: '혈압 관련 주의',
  ),
  ConditionCategory(
    label: '당뇨',
    keyword: '당뇨',
    description: '혈당 영향 약물',
  ),
  ConditionCategory(
    label: '간질환',
    keyword: '간장애',
    description: '간 기능 영향',
  ),
  ConditionCategory(
    label: '신장질환',
    keyword: '신장애',
    description: '신장 기능 영향',
  ),
  ConditionCategory(
    label: '고령자',
    keyword: '고령자',
    description: '어르신 주의 약물',
  ),
  ConditionCategory(
    label: '소아',
    keyword: '소아',
    description: '어린이 주의 약물',
  ),
  ConditionCategory(
    label: '수유부',
    keyword: '수유',
    description: '수유 중 주의 약물',
  ),
  ConditionCategory(
    label: '위장질환',
    keyword: '위장',
    description: '위장 관련 주의',
  ),
  ConditionCategory(
    label: '심장질환',
    keyword: '심장',
    description: '심혈관 영향',
  ),
  ConditionCategory(
    label: '천식',
    keyword: '천식',
    description: '기관지 영향',
  ),
  ConditionCategory(
    label: '알레르기',
    keyword: '알레르기',
    description: '과민반응 주의',
  ),
];
