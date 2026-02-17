import { expect, test } from "@playwright/test";

test("user can map ticker and render analysis result", async ({ page }) => {
  await page.route("**/v1/analyze", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        data: {
          asset: "AAPL",
          source: "stooq",
          symbol: "aapl.us",
          latest_price_date: "2026-01-01",
          current_price: 210.42,
          baseline_4y_ma: 190.12,
          planned_entry_ltv: 0.5,
          stressed_ltv_at_baseline: 0.55,
          max_entry_ltv_for_margin_call: 0.63,
          max_entry_ltv_for_liquidation: 0.72,
          recommended_max_entry_ltv: 0.58,
        },
      }),
    });
  });

  await page.goto("/");

  await page.getByLabel("Ticker").fill("AAPL");
  await page.getByRole("button", { name: "Apply Ticker" }).click();

  await expect(page.getByLabel("Source Symbol")).toHaveValue("aapl.us");

  await page.getByRole("button", { name: "Run Analysis" }).click();

  await expect(page.getByText("Snapshot updated")).toBeVisible();
  await expect(page.getByText("AAPL").first()).toBeVisible();
  await expect(page.getByText("aapl.us").first()).toBeVisible();
});
