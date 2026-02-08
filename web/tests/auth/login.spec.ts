import { test, expect } from "@playwright/test";
import { register, login, randomEmail, APP_URL } from "../helpers/auth";

const seeded = { email: "", nick: "kitty" };

test.beforeAll(async ({ browser }) => {
  const page = await browser.newPage();
  seeded.email = randomEmail("seed");
  await register(page, { nick: seeded.nick, email: seeded.email });
  await page.close();
});

test("existing user can log in", async ({ page }) => {
  await login(page, seeded);
  await expect(page.getByRole("heading", { name: "PurrTasks" })).toBeVisible();
});

test("can switch to Login view and see fields", async ({ page }) => {
  await page.goto(APP_URL);
  await page.getByRole("button", { name: /^Login$/ }).click();

  await expect(page.getByRole("heading", { name: /Sign in/i })).toBeVisible();
  await expect(page.getByLabel("Nickname")).toBeVisible();
  await expect(page.getByLabel("Email")).toBeVisible();
  await expect(page.getByRole("button", { name: /^Log in$/ })).toBeVisible();
});

test("unknown user cannot log in (stays on Sign in)", async ({ page }) => {
  await page.goto(APP_URL);
  await page.getByRole("button", { name: /^Login$/ }).click();

  await page.getByLabel("Nickname").fill("ghost");
  await page.getByLabel("Email").fill(randomEmail("ghost"));
  await page.getByRole("button", { name: /^Log in$/ }).click();

  await expect(page.getByRole("heading", { name: /Sign in/i })).toBeVisible();
});

test("logout returns to auth screen", async ({ page }) => {
  await login(page, seeded);
  await expect(page.getByRole("heading", { name: "PurrTasks" })).toBeVisible();

  const logout = page.getByRole("button", { name: /logout/i });
  await expect(logout).toBeVisible();
  await logout.click();

  await expect(
    page.getByRole("heading", { name: /Create your account|Sign in/i }),
  ).toBeVisible();
});

test("can log in again after logging out", async ({ page }) => {
  await login(page, seeded);
  await expect(page.getByRole("heading", { name: "PurrTasks" })).toBeVisible();

  await page.getByRole("button", { name: /logout/i }).click();

  await login(page, seeded);
  await expect(page.getByRole("heading", { name: "PurrTasks" })).toBeVisible();
});
