import { test, expect, Page } from "@playwright/test";
import { APP_URL, login, randomEmail, register } from "../helpers/auth";

const user = { email: "", nick: "kitty" };
async function createTask(page: Page, title: string) {
  await page.getByRole("textbox", { name: "Title" }).fill(title);
  await page.getByRole("button", { name: "Create" }).click();
  await expect(page.getByText(title)).toBeVisible();
}

function cardByTitle(page: Page, title: string) {
  return page
    .getByRole("listitem")
    .filter({ has: page.getByText(title) })
    .first();
}
// -------------------------------------

test.beforeAll(async ({ browser }) => {
  const page = await browser.newPage();
  user.email = randomEmail("tasks");
  await register(page, { nick: user.nick, email: user.email });
  await page.close();
});

test.beforeEach(async ({ page }) => {
  await login(page, user);
});

test("visible header after login", async ({ page }) => {
  await expect(page.getByRole("heading", { name: "PurrTasks" })).toBeVisible();
});

test("create task, start it and mark as done", async ({ page }) => {
  const title = `task-${Date.now()}`;
  await createTask(page, title);

  const card = cardByTitle(page, title);
  await card.getByRole("button", { name: /^Start$/ }).click();
  await expect(
    card.getByRole("button", { name: /^Done$/, exact: true }),
  ).toBeVisible();
  await card.getByRole("button", { name: /^Done$/, exact: true }).click();
  await expect(card.getByText(/Status:\s*DONE/i)).toBeVisible();
});

test("start task then cancel it", async ({ page }) => {
  const title = `task-${Date.now()}-c`;
  await createTask(page, title);
  const card = cardByTitle(page, title);
  await card.getByRole("button", { name: /^Start$/ }).click();
  await card.getByRole("button", { name: /^Cancel$/, exact: true }).click();
  await expect(card.getByText(/Status:\s*CANCELED/i)).toBeVisible();
});

test("edit task title and save", async ({ page }) => {
  const title = `task-${Date.now()}`;
  const updated = `${title}-upd`;
  await createTask(page, title);
  const card = cardByTitle(page, title);
  await card.getByRole("button", { name: /^Edit$/ }).click();
  await card.getByRole("textbox", { name: /^Title$/ }).fill(updated);
  await card.getByRole("button", { name: /^Save$/ }).click();

  await expect(page.getByText(updated)).toBeVisible();
});

test("delete task removes it from the board", async ({ page }) => {
  const title = `task-${Date.now()}-del`;
  await createTask(page, title);
  const card = cardByTitle(page, title);
  await expect(card).toBeVisible();
  const confirm = page.waitForEvent("dialog").then((d) => d.accept());
  await card.getByRole("button", { name: /^Delete$/ }).click();
  await confirm;
  await expect(page.getByText(title)).toHaveCount(0);
});

test("tabs can be switched (NEW → IN PROGRESS → DONE → CANCELED → ALL)", async ({
  page,
}) => {
  await page.getByRole("button", { name: /^NEW$/i }).click();
  await page.getByRole("button", { name: /^IN PROGRESS$/i }).click();
  await page.getByRole("button", { name: /^DONE$/i }).click();
  await page.getByRole("button", { name: /^CANCELED$/i }).click();
  await page.getByRole("button", { name: /^ALL$/i }).click();
});

test("logout returns to auth screen", async ({ page }) => {
  await page.getByRole("button", { name: /logout/i }).click();
  await expect(
    page.getByRole("heading", { name: /Create your account|Sign in/i }),
  ).toBeVisible();
});
