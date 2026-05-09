import { apiClient } from "@/lib/api-client";
import type { MoneyString } from "@/lib/money";

export type GoalType = "saving" | "live_alone" | "buy_car" | "travel";

export type Goal = {
  id: string;
  goal_type: GoalType;
  name: string;
  target_amount: MoneyString;
  current_amount: MoneyString;
  monthly_contribution: MoneyString;
  target_date: string | null;
  priority: number;
  status: "planning" | "active" | "paused" | "completed" | "not_viable";
  parameters: Record<string, unknown>;
};

export function createGoal(payload: {
  goal_type: "saving" | "live_alone" | "buy_car" | "travel";
  name: string;
  target_amount: MoneyString;
  current_amount?: MoneyString;
  monthly_contribution?: MoneyString;
  target_date?: string;
  priority?: number;
}) {
  return apiClient<Goal>("/goals", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function listGoals() {
  return apiClient<Goal[]>("/goals");
}

export function getGoal(goalId: string) {
  return apiClient<Goal>(`/goals/${goalId}`);
}

export function addGoalContribution(goalId: string, payload: { amount: MoneyString; contribution_date: string }) {
  return apiClient<Goal>(`/goals/${goalId}/contributions`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function deleteGoal(goalId: string) {
  return apiClient<{ status: string }>(`/goals/${goalId}`, {
    method: "DELETE",
  });
}
