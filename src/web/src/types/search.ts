/** 검색 관련 타입 정의. */

export type ItemType = "drug" | "supplement";

export type SearchFilter = "all" | ItemType;

export interface SelectedItem {
  item_type: ItemType;
  item_id: number;
  name: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
}
