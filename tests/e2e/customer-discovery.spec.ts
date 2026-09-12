import { expect, test } from "@playwright/test";

test.describe("Customer discovery", () => {
  test("searches, filters, favorites, and adds a restaurant to cart", async ({ page }) => {
    await page.goto("/");
    await expect(page).toHaveTitle(/FOODFLOW/);
    await expect(page.getByRole("heading", { name: "Good food, good mood." })).toBeVisible();

    const search = page.getByPlaceholder("Search for dishes, restaurants or cuisines");
    await search.fill("pizza");
    await expect(page.getByRole("heading", { name: "Crust & Craft" })).toBeVisible();
    await expect(page.getByRole("heading", { name: "Namma Thindi" })).not.toBeVisible();

    await search.fill("");
    await page.getByRole("button", { name: "South Indian" }).click();
    await expect(page.getByRole("heading", { name: "Namma Thindi" })).toBeVisible();

    const favorite = page.getByRole("button", { name: "Favorite Namma Thindi" });
    await favorite.click();
    await expect(favorite).toHaveClass(/active/);

    await page.locator(".restaurant-card").filter({ hasText: "Namma Thindi" }).getByRole("button", { name: "Add to cart" }).click();
    await expect(page.getByRole("button", { name: /Cart/ })).toContainText("1");
  });
});
