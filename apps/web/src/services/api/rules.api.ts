import { apiClient } from "@/lib/api-client";

export type UserRule = {
  id: string;
  name: string;
  scope: string;
  condition_json: Record<string, unknown>;
  action_json: Record<string, unknown>;
  priority: number;
  version: number;
  is_active: boolean;
};

export type RuleTemplate = {
  id: string;
  code: string;
  name: string;
  description: string | null;
  allowed_fields: string[];
  allowed_operators: string[];
  schema_json: Record<string, unknown>;
};

export function listRuleTemplates() {
  return apiClient<RuleTemplate[]>("/rules/templates");
}

export function listUserRules() {
  return apiClient<UserRule[]>("/rules/custom");
}

export function createUserRule(payload: unknown) {
  return apiClient<UserRule>("/rules/custom", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function updateUserRule(id: string, payload: unknown) {
  return apiClient<UserRule>(`/rules/custom/${id}`, {
    method: "PATCH",
    body: JSON.stringify(payload),
  });
}

export function deleteUserRule(id: string) {
  return apiClient<{ status: string }>(`/rules/custom/${id}`, { method: "DELETE" });
}

export function validateRule(payload: unknown) {
  return apiClient("/rules/custom/validate", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}
