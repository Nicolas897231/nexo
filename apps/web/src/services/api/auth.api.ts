import { apiClient } from "@/lib/api-client";

export type LoginRequest = {
  email: string;
  password: string;
  remember_device: boolean;
};

export function login(payload: LoginRequest) {
  return apiClient("/auth/login", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function register(payload: {
  full_name: string;
  email: string;
  password: string;
  accepted_terms: boolean;
}) {
  return apiClient("/auth/register", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function logout() {
  return apiClient("/auth/logout", {
    method: "POST",
    body: JSON.stringify({}),
  });
}

export function changePassword(payload: { current_password: string; new_password: string }) {
  return apiClient("/auth/change-password", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}
