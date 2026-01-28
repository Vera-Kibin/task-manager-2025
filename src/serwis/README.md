# TaskService — warstwa logiki aplikacji

`TaskService` łączy reguły domeny (User/Task/TaskEvent + PermissionPolicy) z portami
repozytoriów. To **jedyny** punkt modyfikacji stanu: tworzy zadania, przydziela, zmienia
status, aktualizuje, miękko usuwa, filtruje listę i zwraca historię.

## Zależności (wstrzykiwane)

- `UsersRepository` – port: `get(user_id) -> User | None`, `add(User) -> None`
- `TasksRepository` – port: `add(Task)`, `get(id) -> Task | None`, `update(Task)`, `list() -> list[Task]`
- `EventsRepository` – port: `add(TaskEvent)`, `list_for_task(task_id) -> list[TaskEvent]`
- `IdGenerator` – `new_id() -> str` (UUID v4)
- `Clock` – `now() -> datetime`

Dzięki portom w testach unit używany jest wariant **InMemory**, a w integracjach/API – **Mongo**.

## Dozwolone przejścia statusów

| Z \-> Do        | NEW | IN_PROGRESS | DONE | CANCELED |
| --------------- | --- | ----------- | ---- | -------- |
| **NEW**         | –   | ✓           | –    | ✓        |
| **IN_PROGRESS** | –   | –           | ✓    | ✓        |
| **DONE**        | –   | –           | –    | –        |
| **CANCELED**    | –   | –           | –    | –        |

Walidowane przez metodę `_is_valid_transition`.

## API serwisu

### `create_task(actor_id, title, description="", priority="NORMAL") -> Task`

- Wymaga: aktor istnieje i `PermissionPolicy.can_create_task(actor)` (status ACTIVE).
- Walidacja: `title` (1..200), `priority` ∈ {LOW, NORMAL, HIGH}.
- Efekt: `tasks.add(task)`, `events.add(CREATED, meta={"owner": actor.id})`.

### `assign_task(actor_id, task_id, assignee_id) -> Task`

- Wymaga: task/aktor/assignee istnieją; `PermissionPolicy.can_assign(actor, task, assignee)`.
- Efekt: zmiana `assignee_id`, `tasks.update`, `events.add(ASSIGNED, meta={"from","to","by"})`.

### `change_status(actor_id, task_id, new_status) -> Task`

- Wymaga: task/aktor istnieją; `new_status` poprawny; podstawowy dostęp (manager albo owner/assignee).
- Walidacja: dozwolone przejście `_is_valid_transition`; `PermissionPolicy.can_change_status`.
- Efekt: aktualizacja `status`, `events.add(STATUS_CHANGED, meta={"from","to","by"})`.

### `update_task(actor_id, task_id, *, title=None, description=None, priority=None) -> Task`

- Wymaga: task/aktor istnieją.
- Uprawnienia:
  - Manager: zawsze.
  - Użytkownik: **nie** dla DONE/CANCELED; tylko owner lub assignee.
- Walidacja: `title` (1..200) jeśli podany; `priority` poprawna.
- Efekt: modyfikuje tylko przekazane pola; jeżeli są zmiany → `tasks.update` i `events.add(UPDATED, meta={"changes", "by"})`.
- Idempotencja: brak zmian → zwraca oryginalny task (bez eventu).

### `delete_task(actor_id, task_id) -> Task`

- Miękkie usuwanie (`is_deleted=True`).
- Uprawnienia:
  - Manager: zawsze.
  - Owner: tylko jeśli `status != DONE`.
- Idempotencja: ponowny delete zwraca już-usunięty task (bez kolejnego eventu).
- Efekt: `tasks.update`, `events.add(DELETED, meta={"by"})`.

### `list_tasks(actor_id, *, status=None, priority=None) -> list[Task]`

- Widoczność:
  - Manager: wszystkie nieusunięte.
  - Użytkownik: tylko własne (owner/assignee) i nieusunięte.
- Filtry:
  - `status` ∈ {NEW, IN_PROGRESS, DONE, CANCELED}
  - `priority` ∈ {LOW, NORMAL, HIGH}

### `get_events(actor_id, task_id) -> list[TaskEvent]`

- Uprawnienia: Manager albo (owner/assignee) danego zadania.
- Zwraca historię uporządkowaną repozytoryjnie (Mongo: indeks po `task_id,timestamp`).

## Typowe wyjątki (do mapowania w HTTP)

- `ValueError` – np. „Invalid title”, „Unknown priority/status”, „Task/Actor not found”.
- `PermissionError` – np. „User cannot assign…”, „Only owner can delete…”, „Cannot update…”.

## Dlaczego spełnia wymagania

- Logika warunkowa + walidacje w każdej operacji.
- Rejestr historii (TaskEvent) dla audytu.
- Izolacja zewnętrznych zależności (porty + `IdGenerator`/`Clock`) → łatwe mockowanie w unitach.
- Spójne i idempotentne operacje (update/delete).

## Przykład użycia (unit)

```python
from src.serwis.task_service import TaskService
from src.repo.memory_repo import InMemoryUsers, InMemoryTasks, InMemoryEvents
from src.utils.idgen import IdGenerator
from src.utils.clock import Clock
from src.domain.user import User, Role, Status

users, tasks, events = InMemoryUsers(), InMemoryTasks(), InMemoryEvents()
svc = TaskService(users, tasks, events, IdGenerator(), Clock())

users.add(User(id="m1", email="m@ex.com", role=Role.MANAGER, status=Status.ACTIVE))
t = svc.create_task("m1", "Feature A", priority="HIGH")
svc.assign_task("m1", t.id, "m1")
svc.change_status("m1", t.id, "IN_PROGRESS")
```
