# Repo — warstwa dostępu do danych (interfejsy)

Ten moduł definiuje _interfejsy_ repozytoriów używane przez serwis domenowy (`TaskService`).
Dzięki nim logika aplikacji jest niezależna od konkretnego magazynu danych
(In-Memory, MongoDB, inne).

## Co tu jest

- `UsersRepository` — pobieranie i zapisywanie użytkowników.
- `TasksRepository` — CRUD dla zadań (bez logiki filtrów).
- `EventsRepository` — rejestr zdarzeń domenowych powiązanych z zadaniem.

Interfejsy są synchroniczne i opisują **kontrakt** między serwisem a warstwą danych.

## Kontrakty metod

### `UsersRepository`

- `get(user_id: str) -> Optional[User]`  
  Zwraca użytkownika lub `None`, gdy brak.
- `add(user: User) -> None`  
  Zapisuje (upsert po `user.id`). Brak wymogu rzucania wyjątku przy duplikacie.

### `TasksRepository`

- `get(task_id: str) -> Optional[Task]`  
  Zwraca zadanie lub `None`.
- `list() -> List[Task]`  
  Zwraca **wszystkie** zadania (w tym soft-deleted); filtrowanie i widoczność
  to odpowiedzialność serwisu.
- `add(task: Task) -> None`  
  Upsert po `task.id`.
- `update(task: Task) -> None`  
  Nadpisuje istniejący stan zadania.

### `EventsRepository`

- `add(event: TaskEvent) -> None`  
  Dodaje zdarzenie domenowe.
- `list_for_task(task_id: str) -> list[TaskEvent]`  
  Zwraca zdarzenia **dla danego zadania** w **porządku chronologicznym rosnącym**
  (kontrakt oczekiwany przez serwis).

## Jak używa tego serwis

`TaskService` przyjmuje instancje repozytoriów w konstruktorze:

```python
from src.serwis.task_service import TaskService
from src.utils.idgen import IdGenerator
from src.utils.clock import Clock

svc = TaskService(users_repo, tasks_repo, events_repo, IdGenerator(), Clock())
```
