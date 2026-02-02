import type { Task, TaskEvent, Priority, TaskStatus } from "./types";

const json = (r: Response) => r.json();

function headers(actorId?: string) {
  const h: Record<string, string> = { "Content-Type": "application/json" };
  if (actorId) h["X-Actor-Id"] = actorId;
  return h;
}
export function actorId(): string | null {
  return localStorage.getItem("actorId");
}

export function setActorId(id: string) {
  localStorage.setItem("actorId", id);
}

export async function api(path: string, init: RequestInit = {}) {
  const headers = new Headers(init.headers || {});
  headers.set("Content-Type", "application/json");
  const id = actorId();
  if (id) headers.set("X-Actor-Id", id);
  const res = await fetch(`/api${path}`, { ...init, headers });
  const body = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(body.message || body.error || res.statusText);
  return body;
}
export async function createUser(p: {
  id: string;
  email: string;
  role: "USER" | "MANAGER";
  status: "ACTIVE" | "BLOCKED";
  first_name: string;
  last_name: string;
  nickname: string;
}) {
  const r = await fetch("/api/users", {
    method: "POST",
    headers: headers(),
    body: JSON.stringify(p),
  });
  if (!r.ok)
    throw new Error((await r.json()).message || "Failed to create user");
  return r.json();
}

export async function listTasks(
  actorId: string,
  q?: { status?: TaskStatus; priority?: Priority },
): Promise<Task[]> {
  const sp = new URLSearchParams();
  if (q?.status) sp.set("status", q.status);
  if (q?.priority) sp.set("priority", q.priority);
  const r = await fetch(`/api/tasks?${sp.toString()}`, {
    headers: headers(actorId),
  });
  if (!r.ok)
    throw new Error((await r.json()).message || "Failed to load tasks");
  return json(r);
}

export async function createTask(
  actorId: string,
  p: { title: string; description?: string; priority?: Priority },
): Promise<Task> {
  const r = await fetch("/api/tasks", {
    method: "POST",
    headers: headers(actorId),
    body: JSON.stringify(p),
  });
  if (!r.ok)
    throw new Error((await r.json()).message || "Failed to create task");
  return json(r);
}

export async function updateTask(
  actorId: string,
  id: string,
  p: Partial<Pick<Task, "title" | "description">> & { priority?: Priority },
): Promise<Task> {
  const r = await fetch(`/api/tasks/${id}`, {
    method: "PATCH",
    headers: headers(actorId),
    body: JSON.stringify(p),
  });
  if (!r.ok)
    throw new Error((await r.json()).message || "Failed to update task");
  return json(r);
}

export async function deleteTask(actorId: string, id: string): Promise<Task> {
  const r = await fetch(`/api/tasks/${id}`, {
    method: "DELETE",
    headers: headers(actorId),
  });
  if (!r.ok)
    throw new Error((await r.json()).message || "Failed to delete task");
  return json(r);
}

export async function assignTask(
  actorId: string,
  id: string,
  assignee_id: string,
): Promise<Task> {
  const r = await fetch(`/api/tasks/${id}/assign`, {
    method: "POST",
    headers: headers(actorId),
    body: JSON.stringify({ assignee_id }),
  });
  if (!r.ok)
    throw new Error((await r.json()).message || "Failed to assign task");
  return json(r);
}

export async function changeStatus(
  actorId: string,
  id: string,
  status: TaskStatus,
): Promise<Task> {
  const r = await fetch(`/api/tasks/${id}/status`, {
    method: "POST",
    headers: headers(actorId),
    body: JSON.stringify({ status }),
  });
  if (!r.ok)
    throw new Error((await r.json()).message || "Failed to change status");
  return json(r);
}

export async function listEvents(
  actorId: string,
  id: string,
): Promise<TaskEvent[]> {
  const r = await fetch(`/api/tasks/${id}/events`, {
    headers: headers(actorId),
  });
  if (!r.ok)
    throw new Error((await r.json()).message || "Failed to load events");
  return json(r);
}

export async function register(p: {
  first_name: string;
  last_name: string;
  nickname: string;
  email: string;
}) {
  const r = await fetch("/api/register", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(p),
  });
  const body = await r.json();
  if (!r.ok) throw new Error(body.message || "Register failed");
  return body as { id: string; message: string };
}

export async function login(p: { email: string; nickname: string }) {
  const r = await fetch("/api/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(p),
  });
  const body = await r.json();
  if (!r.ok) throw new Error(body.message || "Login failed");
  return body as { id: string; role: "USER" | "MANAGER"; nickname: string };
}
export function clearActorId() {
  localStorage.removeItem("actorId");
}
