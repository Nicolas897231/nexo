import { apiClient } from "@/lib/api-client";
import type { MoneyString } from "@/lib/money";

export function simulateCar(payload: {
  monthly_net_income: MoneyString;
  vehicle_price: MoneyString;
  down_payment: MoneyString;
  monthly_rate: string;
  term_months: number;
}) {
  return apiClient("/simulations/car", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function simulateTravel(payload: Record<string, string | number | null>) {
  return apiClient("/simulations/travel", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}
