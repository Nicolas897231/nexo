import { apiClient, createRequestId } from "@/lib/api-client";
import type { MoneyString } from "@/lib/money";

export type MovementCreateRequest = {
  movement_type: "income" | "expense" | "transfer";
  amount: MoneyString;
  transaction_date: string;
  category_id?: string | null;
  income_source_id?: string | null;
  description?: string;
  is_fixed?: boolean;
  metadata?: Record<string, unknown>;
};

export type Movement = {
  id: string;
  category_id: string | null;
  movement_type: "income" | "expense" | "transfer" | "saving" | "debt_payment";
  type: "income" | "expense" | "transfer" | "saving" | "debt_payment";
  amount: MoneyString;
  currency_code: string;
  transaction_date: string;
  description: string | null;
  is_fixed: boolean;
};

export function createMovement(payload: MovementCreateRequest) {
  return apiClient<Movement>("/movements", {
    method: "POST",
    idempotencyKey: createRequestId(),
    body: JSON.stringify(payload),
  });
}

export function listMovements() {
  return apiClient<Movement[]>("/movements");
}

export function deleteMovement(id: string) {
  return apiClient<{ status: string }>(`/movements/${id}`, {
    method: "DELETE",
  });
}
