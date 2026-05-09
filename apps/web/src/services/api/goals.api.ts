import { apiClient } from "@/lib/api-client";
import type { MoneyString } from "@/lib/money";

export function createGoal(payload: {
  goal_type: "saving" | "live_alone" | "buy_car" | "travel";
  name: string;
  target_amount: MoneyString;
  current_amount?: MoneyString;
  monthly_contribution?: MoneyString;
  target_date?: string;
  priority?: number;
}) {
  return apiClient("/goals", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function listGoals() {
  return apiClient("/goals");
}
