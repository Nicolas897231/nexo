import { apiClient } from "@/lib/api-client";
import type { MoneyString } from "@/lib/money";

export type SimulationResult = Record<string, unknown> & { simulation_id: string };

export function simulateSavings(payload: {
  monthly_net_income: MoneyString;
  target_amount: MoneyString;
  current_amount: MoneyString;
  monthly_contribution: MoneyString;
}) {
  return apiClient<SimulationResult>("/simulations/savings", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function simulateCar(payload: {
  monthly_net_income: MoneyString;
  vehicle_price: MoneyString;
  down_payment: MoneyString;
  monthly_rate: string;
  term_months: number;
  insurance_monthly?: MoneyString;
  fuel_monthly?: MoneyString;
  maintenance_monthly?: MoneyString;
  parking_monthly?: MoneyString;
}) {
  return apiClient<SimulationResult>("/simulations/car", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function simulateLivingAlone(payload: Record<string, string>) {
  return apiClient<SimulationResult>("/simulations/living-alone", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function simulateTravel(payload: Record<string, string | number | null>) {
  return apiClient<SimulationResult>("/simulations/travel", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function convertSimulationToGoal(simulationId: string) {
  return apiClient<{ goal_id: string; status: string }>(`/simulations/${simulationId}/convert-to-goal`, {
    method: "POST",
  });
}
