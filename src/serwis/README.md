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
- Idempotencja: brak zmian -> zwraca oryginalny task (bez eventu).

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

## Wysyłka historii zadania e-mailem (integracja zewnętrzna)

`email_task_history(actor_id, task_id, email) -> bool`

- **Cel**: Przygotowuje treść wiadomości e-mail z historią zdarzeń zadania i deleguje wysyłkę do warstwy integracji (`TaskHistoryEmailer` → `SMTPClient`).
- **Wejście**:
  - `actor_id` — kto żąda wysyłki,
  - `task_id` — którego zadania dotyczy historia,
  - `email` — adres odbiorcy; wymagany.
- **Walidacje / wyjątki**:
  - `ValueError("Missing email")` – gdy email pusty/brak.
  - Uprawnienia i istnienie zadania sprawdza wewnętrznie `get_events(...)` (manager lub owner/assignee).
  - Gdy zadanie nie istnieje po pobraniu zdarzeń → `werkzeug.exceptions.NotFound`.
- **Działanie**:
  1. `events = get_events(actor_id, task_id)` — autoryzacja + historia.
  2. `task = tasks.get(task_id)` — tytuł do tematu/treści.
  3. `event_types = [e.type.name for e in events]`.
  4. `TaskHistoryEmailer().send_task_history(email, task.title, event_types) → bool`.
- **Dlaczego tu**: Spełnia wymaganie „zewnętrzna funkcjonalność, którą można mockować w unit testach” – w testach patchujemy wywołanie SMTP, więc nie ma realnego I/O.

### Przykład użycia (wewnątrz serwisu)

```python
ok = svc.email_task_history(actor_id="u1", task_id="t123", email="owner@example.com")
# ok == True/False (zależnie od SMTPClient.send)
```

### Testy jednostkowe (gdzie szukać / co sprawdzają)

- **`tests/unit/serwis/test_email_history.py`**:
  - „Happy path” – poprawne wywołanie i delegacja do SMTP (mock).
  - Brak e-maila -> `ValueError("Missing email")`.
  - Brak zadania -> `werkzeug.exceptions.NotFound` (stub `get_events`, `tasks.get -> None`).
- **`tests/unit/integrations/test_emailer.py`**:
  - Patch `SMTPClient.send` i asercje argumentów (temat z datą, treść z tytułem i listą eventów).
- **`tests/unit/integrations/test_smtp_stub.py`**:
  - Stub SMTP zwraca `False` (bez I/O).

### (Opcjonalnie) Endpoint HTTP

Jeśli chcesz wystawić to w API:

- **Route**: `POST /api/tasks/<task_id>/email-history`
- **Body**: `{"email": "a@b.c"}`
- **Nagłówek**: `X-Actor-Id: <actor_id>`
- **Odpowiedź**: `200 {"sent": true}` lub odpowiedni błąd (`400` brak pola, `403` brak uprawnień, `404` brak zadania).

W handlerze wystarczy wywołać `svc.email_task_history(actor_id, task_id, email)` i zamapować wyjątki (`ValueError→400`, `PermissionError→403`, `NotFound→404`).
