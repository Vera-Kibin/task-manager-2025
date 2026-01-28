# Domain (Core)

Warstwa domeny jest niezależna od frameworków i I/O. Zawiera wyłącznie model i reguły.

## Klasy i Enumy

- `User(id, email, role: Role, status: Status)`
  - Walidacje: niepusty `id`, poprawny `email`, typy `Role`/`Status`.
  - `Role = {USER, MANAGER}`, `Status = {ACTIVE, BLOCKED}`.
- `Task(...)`
  - Stan zadania: `TaskStatus = {NEW, IN_PROGRESS, DONE, CANCELED}`.
  - Priorytet: `Priority = {LOW, NORMAL, HIGH}`.
  - Walidacje: niepuste `id`/`title`/`owner_id`, ograniczenie długości tytułu, typy enumów, `due_date` jako `datetime|None`.
- `TaskEvent(id, task_id, timestamp, type: EventType, meta: dict)`
  - Historia zmian; `EventType = {CREATED, UPDATED, ASSIGNED, STATUS_CHANGED, DELETED}`.

## Reguły uprawnień (PermissionPolicy)

- `can_create_task(actor)` — tylko `Status.ACTIVE`.
- `can_assign(actor, task, assignee)`
  - Manager może, o ile `assignee` jest `ACTIVE`.
  - Użytkownik: musi być właścicielem (`actor.id == task.owner_id`) i oba konta `ACTIVE`.
- `can_change_status(actor, task, target)`
  - Manager zawsze może.
  - Użytkownik `ACTIVE`: `DONE` tylko assignee, inne statusy owner lub assignee.
- `can_delete(actor, task)`
  - Manager zawsze może.
  - Owner może, jeśli `task.status != DONE`.

> Uwaga: historia zdarzeń jest budowana w serwisie (poza warstwą domeny).
