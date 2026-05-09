import { apiClient } from "@/lib/api-client";

export function getDashboardSummary(month: string) {
  return apiClient(`/dashboard/summary?month=${encodeURIComponent(month)}`);
}

export function getDashboardCashflow(month: string) {
  return apiClient(`/dashboard/cashflow?month=${encodeURIComponent(month)}`);
}
