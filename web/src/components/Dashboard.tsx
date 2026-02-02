import { useEffect, useMemo, useState } from "react";
import {
  actorId,
  listTasks,
  createTask,
  deleteTask,
  changeStatus,
  assignTask,
  updateTask,
} from "../lib/api";
import type { Task, TaskStatus, Priority } from "../lib/types";
import { Stepper, StepperNullable } from "./Stepper";

type View = "ALL" | TaskStatus;

const ORDER: ReadonlyArray<TaskStatus> = [
  "NEW",
  "IN_PROGRESS",
  "DONE",
  "CANCELED",
];
const PRIORITIES: ReadonlyArray<Priority> = ["LOW", "NORMAL", "HIGH"];

function prioBadge(p: Priority) {
  if (p === "HIGH") return "bg-rose-100 text-rose-700";
  if (p === "LOW") return "bg-sky-100 text-sky-700";
  return "bg-slate-100 text-slate-700";
}

export default function Dashboard() {
  const aid = actorId()!;
  const nick = localStorage.getItem("nickname") || "there";
  const today = new Intl.DateTimeFormat(undefined, {
    dateStyle: "full",
  }).format(new Date());

  const [items, setItems] = useState<Task[]>([]);
  const [view, setView] = useState<View>("ALL");
  const [priority, setPriority] = useState<Priority | undefined>();
  const [title, setTitle] = useState("");
  const [newPrio, setNewPrio] = useState<Priority>("NORMAL");
  const [loading, setLoading] = useState(false);
  const [msg, setMsg] = useState<string | null>(null);

  // panel edycji
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editTitle, setEditTitle] = useState("");
  const [editPrio, setEditPrio] = useState<Priority>("NORMAL");

  const load = async () => {
    setLoading(true);
    setMsg(null);
    try {
      const data = await listTasks(aid, { priority }); // status filtrujemy „widokiem”
      setItems(data);
    } catch (e: any) {
      setMsg(e.message || "Failed to load");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load(); /* eslint-disable-next-line */
  }, [priority]);

  const groups = useMemo(() => {
    const m: Record<TaskStatus, Task[]> = {
      NEW: [],
      IN_PROGRESS: [],
      DONE: [],
      CANCELED: [],
    };
    for (const t of items) m[t.status].push(t);
    return m;
  }, [items]);

  const visibleStatuses = view === "ALL" ? ORDER : [view];

  return (
    <div className="mx-auto max-w-6xl">
      {/* HERO – miejsce na gif /public/cat.gif */}
      <header className="mb-6 flex items-center gap-4">
        <img
          src="/cat.gif"
          alt="cat"
          className="h-16 w-16 shrink-0 rounded-full object-cover ring-2 ring-pink-200"
          onError={(e) => (e.currentTarget.style.display = "none")}
        />
        <div className="flex-1">
          <div className="text-sm text-slate-500">{today}</div>
          <h1 className="font-purr text-5xl font-black leading-tight tracking-tight">
            PurrTasks
          </h1>
          <div className="text-slate-600">
            Hello, <b>{nick}</b>! Here are your tasks.
          </div>
        </div>
        <button
          className="btn btn-solid-black btn-lg"
          onClick={() => {
            localStorage.removeItem("actorId");
            localStorage.removeItem("nickname");
            location.reload();
          }}
        >
          Logout
        </button>
      </header>

      {/* Toolbar: widoki + filtr priorytetu (stepper) */}
      <div className="mb-6 flex flex-wrap items-center gap-2">
        <div className="flex flex-wrap gap-2">
          {(["ALL", ...ORDER] as View[]).map((v) => (
            <button
              key={v}
              className={`pill ${view === v ? "pill-active" : "pill-muted"}`}
              onClick={() => setView(v)}
            >
              {v === "ALL" ? "All" : v.replace("_", " ")}
            </button>
          ))}
        </div>

        <div className="ml-auto flex items-center gap-2">
          <StepperNullable
            values={PRIORITIES}
            value={priority}
            onChange={setPriority}
            placeholder="All priorities"
          />
          <button onClick={load} className="btn btn-ghost">
            Refresh
          </button>
        </div>
      </div>

      {/* Create task */}
      <div className="mb-6 rounded-2xl bg-white p-5 shadow">
        <div className="mb-3 text-lg font-semibold">Create task</div>
        <div className="flex flex-col gap-3 md:flex-row md:items-end">
          <label className="flex-1">
            <div className="mb-1 text-sm">Title</div>
            <input
              className="input w-full"
              placeholder="My task…"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
            />
          </label>

          <div>
            <div className="mb-1 text-sm">Priority</div>
            <Stepper
              values={PRIORITIES}
              value={newPrio}
              onChange={setNewPrio}
            />
          </div>

          <button
            className="btn btn-solid-black btn-lg"
            onClick={async () => {
              if (!title.trim()) return setMsg("Title is required");
              setMsg(null);
              try {
                await createTask(aid, {
                  title: title.trim(),
                  priority: newPrio,
                });
                setTitle("");
                await load();
              } catch (e: any) {
                setMsg(e.message);
              }
            }}
          >
            Create
          </button>
        </div>
      </div>

      {msg && <div className="mb-4 text-rose-600">{msg}</div>}
      {loading && <div className="opacity-60">Loading…</div>}

      {/* Sekcje statusów – puste nie są renderowane */}
      {visibleStatuses.map((s) => {
        const list = groups[s];
        if (list.length === 0) return null;

        return (
          <section key={s} className="mb-6">
            <div className="mb-2 flex items-baseline gap-3">
              <h2 className="text-xl font-semibold">{s.replace("_", " ")}</h2>
              <span className="text-slate-500">{list.length}</span>
            </div>

            <ul className="grid gap-3">
              {list.map((t) => {
                const mine = t.assignee_id === aid;
                const isEditing = editingId === t.id;

                // które akcje pokazać (bez „disabled”)
                const actions: Array<
                  "start" | "done" | "cancel" | "delete" | "take"
                > =
                  t.status === "NEW"
                    ? ["start", "delete"]
                    : t.status === "IN_PROGRESS"
                      ? mine
                        ? ["done", "cancel", "delete"]
                        : ["take"]
                      : ["delete"]; // DONE / CANCELED

                return (
                  <li key={t.id} className="rounded-2xl bg-white p-4 shadow">
                    <div className="flex items-start gap-3">
                      <div className="flex-1">
                        <div className="text-lg font-medium">
                          {t.title}
                          <span
                            className={`ml-2 rounded px-2 py-0.5 text-xs ${prioBadge(t.priority)}`}
                          >
                            {t.priority}
                          </span>
                        </div>
                        <div className="mt-1 text-sm opacity-70">
                          Status: <b>{t.status}</b>
                        </div>

                        {/* Panel edycji – rozwijany */}
                        {isEditing && (
                          <div className="mt-3 rounded-xl border border-slate-200 p-3">
                            <div className="mb-2 text-sm font-medium">
                              Edit task
                            </div>
                            <div className="flex flex-col gap-3 md:flex-row md:items-end">
                              <label className="flex-1">
                                <div className="mb-1 text-sm">Title</div>
                                <input
                                  className="input w-full"
                                  value={editTitle}
                                  onChange={(e) => setEditTitle(e.target.value)}
                                />
                              </label>
                              <div>
                                <div className="mb-1 text-sm">Priority</div>
                                <Stepper
                                  values={PRIORITIES}
                                  value={editPrio}
                                  onChange={setEditPrio}
                                />
                              </div>
                              <div className="flex gap-2">
                                <button
                                  className="btn btn-solid-black"
                                  onClick={async () => {
                                    try {
                                      await updateTask(aid, t.id, {
                                        title: editTitle.trim(),
                                        priority: editPrio,
                                      });
                                      setEditingId(null);
                                      await load();
                                    } catch (e: any) {
                                      setMsg(e.message);
                                    }
                                  }}
                                >
                                  Save
                                </button>
                                <button
                                  className="btn btn-ghost"
                                  onClick={() => setEditingId(null)}
                                >
                                  Cancel
                                </button>
                              </div>
                            </div>
                          </div>
                        )}
                      </div>

                      <div className="flex flex-wrap gap-2">
                        {/* EDIT */}
                        <button
                          className="btn btn-ghost"
                          onClick={() => {
                            setEditingId(t.id);
                            setEditTitle(t.title);
                            setEditPrio(t.priority);
                          }}
                        >
                          Edit
                        </button>

                        {/* AKCJE – tylko te, które mają sens */}
                        {actions.includes("start") && (
                          <button
                            className="btn btn-outline-slate"
                            onClick={async () => {
                              try {
                                await assignTask(aid, t.id, aid);
                                await changeStatus(aid, t.id, "IN_PROGRESS");
                                await load();
                              } catch (e: any) {
                                setMsg(e.message);
                              }
                            }}
                          >
                            Start
                          </button>
                        )}

                        {actions.includes("done") && (
                          <button
                            className="btn btn-outline-emerald"
                            onClick={async () => {
                              try {
                                await changeStatus(aid, t.id, "DONE");
                                await load();
                              } catch (e: any) {
                                setMsg(e.message);
                              }
                            }}
                          >
                            Done
                          </button>
                        )}

                        {actions.includes("cancel") && (
                          <button
                            className="btn btn-outline-amber"
                            onClick={async () => {
                              try {
                                await changeStatus(aid, t.id, "CANCELED");
                                await load();
                              } catch (e: any) {
                                setMsg(e.message);
                              }
                            }}
                          >
                            Cancel
                          </button>
                        )}

                        {actions.includes("take") && (
                          <button
                            className="btn btn-ghost"
                            title="Assign to me"
                            onClick={async () => {
                              try {
                                await assignTask(aid, t.id, aid);
                                await load();
                              } catch (e: any) {
                                setMsg(e.message);
                              }
                            }}
                          >
                            Take
                          </button>
                        )}

                        {actions.includes("delete") && (
                          <button
                            className="btn btn-outline-rose"
                            onClick={async () => {
                              if (!confirm("Delete task?")) return;
                              try {
                                await deleteTask(aid, t.id);
                                await load();
                              } catch (e: any) {
                                setMsg(e.message);
                              }
                            }}
                          >
                            Delete
                          </button>
                        )}
                      </div>
                    </div>
                  </li>
                );
              })}
            </ul>
          </section>
        );
      })}
    </div>
  );
}
