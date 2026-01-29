# Testy jednostkowe repozytorium (in-memory)

Zestaw testów weryfikuje implementację in-memory warstwy dostępu do danych (`src/repo/memory_repo.py`) niezależnie od serwisu. Testy sprawdzają zgodność z kontraktami zdefiniowanymi w `src/repo/interface.py`.

---

## Co weryfikujemy

### UsersRepository (`InMemoryUsers`)

- **`add(user)`**  
  Zapisuje/aktualizuje użytkownika pod `user.id`.
- **`get(user_id)`**  
  Zwraca obiekt lub `None` dla nieistniejącego.

### TasksRepository (`InMemoryTasks`)

- **`add(task)`**  
  Dodaje zadanie.
- **`get(task_id)`**  
  Zwraca obiekt lub `None`.
- **`update(task)`**  
  Nadpisuje istniejący stan.
- **`list()`**  
  Zwraca wszystkie zadania (bez filtrów) oraz kopię listy — modyfikacja wyniku nie psuje stanu repo.

### EventsRepository (`InMemoryEvents`)

- **`add(event)`**  
  Dopisuje zdarzenie do odpowiedniego `task_id`.
- **`list_for_task(task_id)`**  
  Filtruje wyłącznie zdarzenia danego zadania,
  zwraca w porządku chronologicznym rosnącym po timestamp (ważne dla stabilności historii i spójności z produkcyjnymi backendami).

Uwaga: kolejność dodawania nie zawsze pokrywa się z czasem powstania zdarzeń (mogą być wstawione „z tyłu”). Dlatego test wymusza oczekiwanie na sortowanie po timestamp.

---

## Struktura testów

- **`test_users_repo.py`** — dodawanie/pobieranie użytkowników, przypadek „brak wpisu”.
- **`test_tasks_repo.py`** — dodawanie/pobieranie/aktualizacja/listowanie zadań; sprawdzenie, że `list()` zwraca kopię.
- **`test_events_repo.py`** — filtrowanie po `task_id` i sortowanie po czasie.

---

## Jak uruchomić

```bash
# tylko testy repo
python3 -m pytest tests/unit/repo -q

# z pokryciem (dla całego src/)
python3 -m coverage run --source=src -m pytest tests/unit/repo
python3 -m coverage report -m
```

---

## Kiedy te testy pomagają

- Przy refaktorze implementacji in-memory,
- Podczas dodania innego backendu (np. Mongo) – nowa implementacja musi spełniać te same kontrakty, w szczególności kolejność chronologiczną w `list_for_task`.

---

## Mongo — mapowania (bez I/O)

Testy w `tests/unit/repo/test_mongo_mappings.py` weryfikują funkcje mapujące w `src/repo/mongo_repo.py` bez łączenia z MongoDB:

- **User ⇄ dokument**: `_user_to_doc` / `_doc_to_user`.
- **Task ⇄ dokument**: `_task_to_doc` / `_doc_to_task` (w tym pola opcjonalne i `is_deleted`).
- **TaskEvent ⇄ dokument**: `_event_to_doc` / `_doc_to_event` (w tym domyślne `meta={}`).

### Dlaczego

Stabilność schematu zapisu/odczytu i zgodność enumów (`Role`, `Status`, `TaskStatus`, `Priority`) niezależnie od backendu.

### Uruchomienie

```bash
python3 -m pytest tests/unit/repo/test_mongo_mappings.py -q
```

---

## Mongo — implementacja (fakes)

Testy w `tests/unit/repo/test_mongo_repo_units.py` weryfikują klasy `MongoUsers`, `MongoTasks`, `MongoEvents` bez prawdziwego MongoDB, używając fałszywego klienta i kolekcji:

- **CRUD użytkowników/zadań**: `add`, `get`, `update`, `list`.
- **Sortowanie zdarzeń**: `list_for_task` (po `timestamp`).
- **Indeksy**: Tworzenie indeksu złożonego w `MongoEvents` (`create_index([("task_id", ASC), ("timestamp", ASC)])`).

### Jak to działa

- FakeMongoClient, FakeDB, FakeCollection, FakeCursor symulują zachowanie MongoDB.
- Testy patchują `mongo_repo.MongoClient = FakeMongoClient` i ustawiają zmienne środowiskowe (`MONGO_URI`, `MONGO_DB`) dla ścieżki „domyślnej”.

### Uruchomienie

```bash
python3 -m pytest tests/unit/repo/test_mongo_repo_units.py -q
# albo cała paczka unitów repo:
python3 -m pytest tests/unit/repo -q
```

---

## Notka

Obie grupy testów nie wymagają uruchomionej bazy ani Dockera. Testy API z Mongo są osobnym tematem i będą uruchamiane przez CI z docker-compose.
