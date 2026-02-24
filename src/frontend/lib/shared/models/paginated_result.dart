/// 페이지네이션 응답 모델.
class PaginatedResult<T> {
  /// 현재 페이지의 아이템 목록.
  final List<T> items;

  /// 전체 아이템 수.
  final int total;

  /// 현재 페이지 번호.
  final int page;

  /// 페이지당 아이템 수.
  final int pageSize;

  /// 전체 페이지 수.
  final int totalPages;

  /// [PaginatedResult] 생성자.
  const PaginatedResult({
    required this.items,
    required this.total,
    required this.page,
    required this.pageSize,
    required this.totalPages,
  });

  /// JSON에서 [PaginatedResult]를 생성한다.
  ///
  /// [json] 은 `{ items, total, page, page_size, total_pages }` 형태.
  /// [itemFromJson] 은 각 아이템을 변환하는 콜백.
  factory PaginatedResult.fromJson(
    Map<String, dynamic> json,
    T Function(Map<String, dynamic>) itemFromJson,
  ) {
    return PaginatedResult(
      items: (json['items'] as List)
          .map((e) => itemFromJson(e as Map<String, dynamic>))
          .toList(),
      total: json['total'] as int,
      page: json['page'] as int,
      pageSize: json['page_size'] as int,
      totalPages: json['total_pages'] as int,
    );
  }
}
