# Repo — warstwa dostępu do danych

Moduł definiuje **interfejsy** repozytoriów używane przez serwis domenowy (`TaskService`) oraz ich prostą implementację **in-memory** do pracy lokalnej i testów. Dzięki temu logika aplikacji jest niezależna od konkretnego magazynu danych (In-Memory, MongoDB, itp.).

---

## Interfejsy (kontrakty)

Plik: `src/repo/interface.py`

- **`UsersRepository`** — pobieranie i zapisywanie użytkowników.
  - `get(user_id: str) -> Optional[User]`
  - `add(user: User) -> None`

- **`TasksRepository`** — podstawowe operacje na zadaniach.
  - `get(task_id: str) -> Optional[Task]`
  - `list() -> List[Task]` — zwraca _wszystkie_ zadania (filtrowanie/widoczność realizuje serwis).
  - `add(task: Task) -> None`
  - `update(task: Task) -> None`

- **`EventsRepository`** — rejestr zdarzeń domenowych.
  - `add(event: TaskEvent) -> None`
  - `list_for_task(task_id: str) -> list[TaskEvent]` — zwrot w porządku chronologicznym rosnącym (oczekiwany przez serwis).

Interfejsy są synchroniczne i opisują **kontrakt** między serwisem a warstwą danych.

---

## Implementacja in-memory (dev/test)

Plik: `src/repo/memory_repo.py`

- **`InMemoryUsers`**
  - Słownik `id -> User`.
  - `get` zwraca `None`, gdy brak; `add` to upsert po `user.id`.

- **`InMemoryTasks`**
  - Słownik `id -> Task`.
  - `list()` zwraca kopię wartości (lista), bez filtrowania i bez ukrywania soft-deleted — to robi serwis.

- **`InMemoryEvents`**
  - Mapa `task_id -> [TaskEvent]`.
  - `add` dopisuje na koniec; `list_for_task` zwraca wyłącznie zdarzenia danego zadania w kolejności dodania
    (dla naszego serwisu ≈ kolejność czasowa; w repo produkcyjnym należy gwarantować sortowanie po `timestamp`).

**Uwagi implementacyjne**

- Operacje mają złożoność ~O(1) na dostęp/aktualizację (tablice haszujące).
- `update(task)` nie sprawdza istnienia — nadpisuje stan pod `task.id` (zgodnie z kontraktem).
- Brak trwałości i współdzielenia między procesami; to implementacja do lokalnego dev/testów.

---

## Jak używa tego serwis

`TaskService` przyjmuje instancje repozytoriów w konstruktorze:

```python
from src.serwis.task_service import TaskService
from src.utils.idgen import IdGenerator
from src.utils.clock import Clock

svc = TaskService(users_repo, tasks_repo, events_repo, IdGenerator(), Clock())
```
