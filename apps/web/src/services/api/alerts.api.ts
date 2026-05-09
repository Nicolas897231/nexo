import { apiClient } from "@/lib/api-client";

export type Alert = {
  id: string;
  goal_id: string | null;
  alert_type: string;
  severity: "info" | "warning" | "danger";
  message: string;
  payload: Record<string, unknown> | null;
  status: string;
  created_at: string;
};

export function listAlerts() {
  return apiClient<Alert[]>("/alerts");
}

export function markAlertRead(id: string) {
  return apiClient<{ status: string }>(`/alerts/${id}/read`, { method: "PATCH" });
}
