import { apiClient } from "@/lib/api-client";
import type { MoneyString } from "@/lib/money";

export type FinancialProfile = {
  monthly_income: MoneyString;
  currency_code: string;
  city: string | null;
  payday: number | null;
  paydays: number[] | null;
  income_frequency: "monthly" | "biweekly" | "weekly" | "variable" | null;
};

export type FinancialProfilePayload = {
  monthly_income?: MoneyString;
  currency_code?: string;
  city?: string;
  payday?: number | null;
  paydays?: number[];
  income_frequency?: "monthly" | "biweekly" | "weekly" | "variable";
};

export function getFinancialProfile() {
  return apiClient<FinancialProfile>("/financial-profile");
}

export function updateFinancialProfile(payload: FinancialProfilePayload) {
  return apiClient<FinancialProfile>("/financial-profile", {
    method: "PATCH",
    body: JSON.stringify(payload),
  });
}
