import { apiClient } from "@/lib/api-client";

export type CategoryKind = "income" | "expense" | "saving" | "debt";

export type Category = {
  id: string;
  user_id: string | null;
  name: string;
  kind: CategoryKind;
  parent_id: string | null;
};

export function listCategories() {
  return apiClient<Category[]>("/categories");
}
