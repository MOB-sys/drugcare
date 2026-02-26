/** 복약함 관련 타입 정의. */

export interface CabinetItem {
  id: number;
  device_id: string;
  item_type: "drug" | "supplement";
  item_id: number;
  item_name: string;
  nickname: string | null;
  created_at: string;
}

export interface CabinetItemCreate {
  item_type: "drug" | "supplement";
  item_id: number;
  nickname?: string;
}
