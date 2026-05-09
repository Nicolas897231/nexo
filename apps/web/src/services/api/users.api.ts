import { apiClient } from "@/lib/api-client";

export function getMe() {
  return apiClient("/users/me");
}

export function updatePreferences(payload: unknown) {
  return apiClient("/users/me/preferences", {
    method: "PATCH",
    body: JSON.stringify(payload),
  });
}
