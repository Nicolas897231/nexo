import { apiClient } from "@/lib/api-client";
import type { MoneyString } from "@/lib/money";

export type DashboardSummary = {
  period_month: string;
  total_income: MoneyString;
  total_expenses: MoneyString;
  debt_payments: MoneyString;
  savings_amount: MoneyString;
  available_cashflow: MoneyString;
  active_goals: number;
  active_alerts: number;
};

export type CashflowPoint = {
  date: string;
  movement_type: string;
  amount: MoneyString;
};

export function getDashboardSummary(month: string) {
  return apiClient<DashboardSummary>(`/dashboard/summary?month=${encodeURIComponent(month)}`);
}

export function getDashboardCashflow(month: string) {
  return apiClient<CashflowPoint[]>(`/dashboard/cashflow?month=${encodeURIComponent(month)}`);
}
