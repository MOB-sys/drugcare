/** 상호작용 체크 API. */

import { fetchApi } from "./client";
import type { InteractionCheckItem, InteractionCheckResponse } from "@/types/interaction";

export function checkInteractions(
  items: InteractionCheckItem[],
): Promise<InteractionCheckResponse> {
  if (items.length < 2) {
    throw new Error("상호작용 체크에는 최소 2개 항목이 필요합니다.");
  }
  return fetchApi<InteractionCheckResponse>("/api/v1/interactions/check", {
    method: "POST",
    body: JSON.stringify({ items }),
  });
}
