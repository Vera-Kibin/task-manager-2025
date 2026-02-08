import { test, expect } from "@playwright/test";
import { register, randomEmail, APP_URL } from "../helpers/auth";

test("user can register", async ({ page }) => {
  const email = randomEmail("cat");
  await register(page, { nick: "kitty", email });

  await expect(page.getByRole("heading", { name: "PurrTasks" })).toBeVisible();
});

test("default screen is Register form", async ({ page }) => {
  await page.goto(APP_URL);
  await expect(
    page.getByRole("heading", { name: /Create your account/i }),
  ).toBeVisible();
  await expect(page.getByLabel("First name")).toBeVisible();
  await expect(page.getByLabel("Last name")).toBeVisible();
  await expect(page.getByLabel("Nickname")).toBeVisible();
  await expect(page.getByLabel("Email")).toBeVisible();
  await expect(
    page.locator("form").getByRole("button", { name: "Register" }),
  ).toBeVisible();
});

test("can switch to Login form nad back to Register", async ({ page }) => {
  await page.goto(APP_URL);
  await page.getByRole("button", { name: /^Login$/ }).click();
  await expect(page.getByRole("button", { name: /^Log in$/ })).toBeVisible();
  await page.getByRole("button", { name: /^Register$/ }).click();
  await expect(
    page.locator("form").getByRole("button", { name: "Register" }),
  ).toBeVisible();
});
