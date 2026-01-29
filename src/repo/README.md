# Repo — warstwa dostępu do danych

Warstwa danych zdefiniowana przez interfejsy oraz dwie implementacje: in-memory (dev/test) i MongoDB (trwała). Logika domenowa (`TaskService`) nie zależy od konkretnego magazynu.

---

## Interfejsy (kontrakty)

**Plik**: `src/repo/interface.py`

- **`UsersRepository`**:
  - `get(user_id) -> Optional[User]`
  - `add(user) -> None`
- **`TasksRepository`**:
  - `get(task_id) -> Optional[Task]`
  - `list() -> List[Task]`
  - `add(task) -> None`
  - `update(task) -> None`
- **`EventsRepository`**:
  - `add(event) -> None`
  - `list_for_task(task_id) -> List[TaskEvent]` — zwrot w porządku chronologicznie rosnącym po `timestamp`.

Interfejsy są synchroniczne i stanowią kontrakt dla implementacji.

---

## Implementacja in-memory (dev/test)

**Plik**: `src/repo/memory_repo.py`

- **`InMemoryUsers`** — słownik `id → User`, upsert w `add`.
- **`InMemoryTasks`** — słownik `id → Task`, `list()` zwraca kopię (bez filtrów; widoczność/filtrowanie robi serwis).
- **`InMemoryEvents`** — mapa `task_id → [TaskEvent]`;  
  `list_for_task()` sortuje po `timestamp` (stabilna kolejność historii, spójna z backendami produkcyjnymi).

**Uwagi**:  
Operacje ~O(1), brak trwałości/współdzielenia, implementacja tylko do lokalnego dev/test.

---

## Implementacja MongoDB

**Plik**: `src/repo/mongo_repo.py`

### Mapowania (funkcje pomocnicze)

- **User ⇄ dokument**: `_user_to_doc` / `_doc_to_user`
- **Task ⇄ dokument**: `_task_to_doc` / `_doc_to_task` (obsługa pól opcjonalnych i `is_deleted`)
- **TaskEvent ⇄ dokument**: `_event_to_doc` / `_doc_to_event` (`meta` domyślnie `{}`)

### Repozytoria

- **`MongoUsers`** — `get`, `add` (upsert po `_id`)
- **`MongoTasks`** — `add/update` (upsert po `_id`), `get`, `list`
- **`MongoEvents`** — `add`, `list_for_task` z sortowaniem po `timestamp` oraz indeks złożony:  
  `create_index([("task_id", ASCENDING), ("timestamp", ASCENDING)])`

### Wymagania / konfiguracja

- **Biblioteka**: `pymongo` (zdefiniowana w `requirements.txt`)
- **Zmienne środowiskowe**:
  - `MONGO_URI` (domyślnie `mongodb://localhost:27017`)
  - `MONGO_DB` (domyślnie `taskmgr`)

---

## Integracja z serwisem

```python
from src.serwis.task_service import TaskService
from src.utils.idgen import IdGenerator
from src.utils.clock import Clock

svc = TaskService(users_repo, tasks_repo, events_repo, IdGenerator(), Clock())
```

W API (`app/api.py`) backend wybierany przez `STORAGE`:

- `STORAGE=memory` → `InMemory*`
- `STORAGE=mongo` → `Mongo*` (używa `MONGO_URI`, `MONGO_DB`)

---

## Testy

- **In-memory**:
  - `tests/unit/repo/test_users_repo.py`
  - `test_tasks_repo.py`
  - `test_events_repo.py`
- **Mongo — mapowania (bez I/O)**:
  - `tests/unit/repo/test_mongo_mappings.py`  
    _(pytest.importorskip("pymongo"))_
- **Mongo — implementacja z „fakes”**:
  - `tests/unit/repo/test_mongo_repo_units.py`  
    _(fałszywy klient/kolekcje; bez Dockera)_

### Uruchomienie przykładowe

```bash
python3 -m pytest tests/unit/repo -q
# lub tylko Mongo:
python3 -m pytest tests/unit/repo/test_mongo_mappings.py tests/unit/repo/test_mongo_repo_units.py -q
```

---

## Uwagi

- `list_for_task()` musi gwarantować porządek rosnący po `timestamp` w każdej implementacji.
- `due_date` jest przechowywane jako `datetime` (bez strefy czasowej); jeśli w przyszłości zmienisz format (np. ISO-8601), zaktualizuj mapowania i testy.
- Operacje `add/update` są idempotentne (upsert).
