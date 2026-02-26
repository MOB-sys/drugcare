/** 상호작용 체크 API. */

import { fetchApi } from "./client";
import type { InteractionCheckItem, InteractionCheckResponse } from "@/types/interaction";

export function checkInteractions(
  items: InteractionCheckItem[],
): Promise<InteractionCheckResponse> {
  return fetchApi<InteractionCheckResponse>("/api/v1/interactions/check", {
    method: "POST",
    body: JSON.stringify({ items }),
  });
}
