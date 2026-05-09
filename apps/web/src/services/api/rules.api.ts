import { apiClient } from "@/lib/api-client";

export function listRuleTemplates() {
  return apiClient("/rules/templates");
}

export function validateRule(payload: unknown) {
  return apiClient("/rules/custom/validate", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}
