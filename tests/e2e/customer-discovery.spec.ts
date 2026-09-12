import { expect, test } from "@playwright/test";

test.describe("Customer discovery", () => {
  test("searches, filters, favorites, and adds a restaurant to cart", async ({ page }) => {
    await page.goto("/");
    await expect(page).toHaveTitle(/FOODFLOW/);
    await page.getByRole("button", { name: "Get Started" }).click();
    await expect(page.getByRole("heading", { name: "Good food, good mood." })).toBeVisible();

    const search = page.getByPlaceholder("Search restaurants, dishes or cuisines");
    await search.fill("pizza");
    await expect(page.getByRole("button", { name: "Chianti", exact: true })).toBeVisible();
    await expect(page.getByRole("button", { name: "Meghana Foods", exact: true })).not.toBeVisible();

    await search.fill("");
    await page.getByRole("button", { name: "South Indian" }).click();
    await expect(page.getByRole("button", { name: "MTR 1924", exact: true })).toBeVisible();

    const favorite = page.getByRole("button", { name: "Favorite MTR 1924" });
    await favorite.click();
    await expect(favorite).toHaveClass(/active/);

    await page.getByRole("button", { name: "Log in" }).click();
    await expect(page.getByRole("heading", { name: "Welcome back" })).toBeVisible();
    await page.getByRole("button", { name: "Log in to Foodflow" }).click();
    await expect(page.getByRole("button", { name: "Aarav" })).toBeVisible();

    await page.locator(".restaurant-card").filter({ hasText: "MTR 1924" }).getByRole("button", { name: "View menu" }).click();
    await page.getByRole("button", { name: "Add", exact: true }).first().click();
    await page.getByRole("button", { name: "Close menu" }).click();
    await page.getByRole("button", { name: /Cart/ }).click();
    await page.getByRole("button", { name: "Continue to checkout" }).click();
    await expect(page.getByRole("heading", { name: "Checkout" })).toBeVisible();
    await page.getByRole("button", { name: "Place demo order" }).click();
    await expect(page.getByRole("heading", { name: "Your kitchen is on it." })).toBeVisible();
  });
});
