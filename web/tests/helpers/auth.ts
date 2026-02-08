import { expect, Page } from "@playwright/test";

export const APP_URL = "http://localhost:5173/";

export const randomEmail = (prefix = "user") =>
  `${prefix}+${Date.now()}@example.com`;
export async function switchToLogin(page: Page) {
  const onRegister = await page
    .getByRole("heading", { name: /Create your account/i })
    .isVisible()
    .catch(() => false);

  if (onRegister) {
    await page.getByRole("button", { name: /^Login$/ }).click();
    await expect(page.getByRole("heading", { name: /Sign in/i })).toBeVisible();
  }
}
export async function register(
  page: Page,
  {
    first = "cat",
    last = "cat",
    nick = "kitty",
    email,
  }: { first?: string; last?: string; nick: string; email: string },
) {
  await page.goto(APP_URL);
  await page.getByRole("textbox", { name: "First name" }).fill(first);
  await page.getByRole("textbox", { name: "Last name" }).fill(last);
  await page.getByRole("textbox", { name: "Nickname" }).fill(nick);
  await page.getByRole("textbox", { name: "Email" }).fill(email);
  await page.locator("form").getByRole("button", { name: "Register" }).click();
}

export async function login(
  page: Page,
  { email, nick }: { email: string; nick: string },
) {
  await page.goto(APP_URL);
  await switchToLogin(page);

  await page.getByRole("textbox", { name: "Nickname" }).fill(nick);
  await page.getByRole("textbox", { name: "Email" }).fill(email);
  await page.getByRole("button", { name: /^Log in$/ }).click();
}
