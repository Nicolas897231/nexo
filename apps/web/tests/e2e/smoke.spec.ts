import { expect, test } from "@playwright/test";

test("dashboard renders the main navigation and KPI cards", async ({ page }) => {
  await page.context().addCookies([
    {
      name: "access_token",
      value: "e2e-placeholder",
      domain: "127.0.0.1",
      path: "/",
    },
  ]);
  await page.goto("/dashboard");
  await expect(page.getByRole("link", { name: /NexoVia/i })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Dashboard" })).toBeVisible();
  await expect(page.getByText("Ingresos del mes")).toBeVisible();
});

test("movements drawer opens from query params", async ({ page }) => {
  await page.context().addCookies([
    {
      name: "access_token",
      value: "e2e-placeholder",
      domain: "127.0.0.1",
      path: "/",
    },
  ]);
  await page.goto("/movements?drawer=create&type=expense");
  await expect(page.getByRole("heading", { name: "Registrar movimiento" })).toBeVisible();
  await expect(page.getByText("Registrar gasto")).toBeVisible();
});
