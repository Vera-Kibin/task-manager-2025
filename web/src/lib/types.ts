export type Role = "USER" | "MANAGER";
export type Status = "ACTIVE" | "BLOCKED";
export type Priority = "LOW" | "NORMAL" | "HIGH";
export type TaskStatus = "NEW" | "IN_PROGRESS" | "DONE" | "CANCELED";

export interface Task {
  id: string;
  title: string;
  description: string;
  status: TaskStatus;
  priority: Priority;
  owner_id: string;
  assignee_id?: string | null;
  due_date?: string | null;
  is_deleted?: boolean;
}

export interface TaskEvent {
  id: string;
  task_id: string;
  timestamp: string;
  type: "CREATED" | "ASSIGNED" | "STATUS_CHANGED" | "UPDATED" | "DELETED";
  meta: Record<string, unknown>;
}
