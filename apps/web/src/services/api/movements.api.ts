import { apiClient } from "@/lib/api-client";
import type { MoneyString } from "@/lib/money";

export type MovementCreateRequest = {
  movement_type: "income" | "expense" | "transfer";
  amount: MoneyString;
  transaction_date: string;
  category_id?: string | null;
  income_source_id?: string | null;
  description?: string;
};

export function createMovement(payload: MovementCreateRequest) {
  return apiClient("/movements", {
    method: "POST",
    idempotencyKey: crypto.randomUUID(),
    body: JSON.stringify(payload),
  });
}

export function listMovements() {
  return apiClient("/movements");
}
