/** 복약함 API 모듈. */

import { fetchApi } from "./client";
import type { CabinetItem, CabinetItemCreate } from "@/types/cabinet";

/** 복약함 목록 조회. */
export async function getCabinetItems(): Promise<CabinetItem[]> {
  return fetchApi<CabinetItem[]>("/api/v1/cabinet");
}

/** 복약함에 아이템 추가. */
export async function addCabinetItem(
  body: CabinetItemCreate,
): Promise<CabinetItem> {
  return fetchApi<CabinetItem>("/api/v1/cabinet", {
    method: "POST",
    body: JSON.stringify(body),
  });
}

/** 복약함에서 아이템 삭제. */
export async function deleteCabinetItem(id: number): Promise<void> {
  await fetchApi<null>(`/api/v1/cabinet/${id}`, { method: "DELETE", allowNullData: true });
}
