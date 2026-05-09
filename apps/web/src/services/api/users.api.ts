import { apiClient } from "@/lib/api-client";

export type UserMe = {
  id: string;
  email: string;
  status: string;
  profile: {
    first_name: string | null;
    last_name: string | null;
    country_code: string | null;
    city: string | null;
    currency_code: string | null;
    payday: number | null;
    paydays: number[] | null;
    income_frequency: "monthly" | "biweekly" | "weekly" | "variable" | null;
  };
};

export type UserSettings = {
  theme_mode: "system" | "light" | "dark";
  accent_color: string;
  dashboard_layout: Record<string, unknown>;
  notification_settings: Record<string, unknown>;
};

export function getMe() {
  return apiClient<UserMe>("/users/me");
}

export function updateProfile(payload: Partial<UserMe["profile"]>) {
  return apiClient<UserMe>("/users/me", {
    method: "PATCH",
    body: JSON.stringify(payload),
  });
}

export function getPreferences() {
  return apiClient<UserSettings>("/users/me/preferences");
}

export function updatePreferences(payload: unknown) {
  return apiClient<UserSettings>("/users/me/preferences", {
    method: "PATCH",
    body: JSON.stringify(payload),
  });
}
