# Task Manager 2025

**Autor:** Vera Kibin  
**Grupa:** 2

Aplikacja backendowa (Flask) do zarządzania zadaniami. Logika domenowa jest odseparowana od warstwy danych dzięki interfejsom repozytoriów. Dostępne są dwa backendy: in-memory (dev/test) i MongoDB (trwała). Do projektu dołączono pełny zestaw testów: unit, API, BDD oraz performance, a także komplet workflowów CI.

---

## 1. Co spełnia wymagania

### Funkcjonalności (≥6)

- **Tworzenie zadań** z walidacją pól (`title`, `priority`).
- **Przypisywanie zadań** z kontrolą uprawnień (`owner`/`manager`).
- **Zmiany statusu** z dozwolonymi przejściami (`NEW -> IN_PROGRESS -> DONE/CANCELED`).
- **Aktualizacja pól** (`tytuł`/`opis`/`priorytet`) z walidacją i ograniczeniami (np. brak zmian -> brak eventu).
- **Miękkie usuwanie** (`is_deleted=True`) + idempotencja.
- **Listowanie** z filtrami (`status`, `priority`) i widocznością per rola/relacja.
- **Rejestr historii** (zdarzenia `CREATED`/`ASSIGNED`/`STATUS_CHANGED`/`UPDATED`/`DELETED`).
- **Wysyłka historii e-mailem** (warstwa integracyjna, mockowana w unitach).

### Klasy współpracujące (≥3)

- **`TaskService`** (logika aplikacji),
- **`UsersRepository` / `TasksRepository` / `EventsRepository`** (porty + implementacje in-memory/Mongo),
- **Modele domenowe:** `User`, `Task`, `TaskEvent`, `PermissionPolicy`.

### Funkcjonalność zależna od danych użytkownika

- **Uprawnienia** wynikające z roli/statusu (`Role`, `Status`) oraz relacji do zadania (`owner`/`assignee`).

### Zewnętrzna funkcjonalność (mockowana w unitach)

- **SMTP:** `TaskHistoryEmailer` + `SMTPClient` (stub) — testy mockują `.send(...)`.
- **Generatory/źródła czasu:** `IdGenerator.new_id()` i `Clock.now()` — mockowane w unitach.
- **Zewnętrzna baza:** alternatywny backend MongoDB (w unitach weryfikowane mapowania + fakes).

---

## 2. Mini-demo (wideo)

Poniżej znajdują się krótkie klipy wideo demonstrujące kluczowe funkcjonalności aplikacji.  
Wideo są hostowane w katalogu `docs/media` lub na GitHub Issues.

1. **Rejestracja**  
   <video src="https://github.com/Vera-Kibin/task-manager-2025/issues/26#issue-3911766019" width="900" controls></video>  
   Wypełnienie formularza i przejście do widoku “PurrTasks”.

2. **Utworzenie zadania**  
   <video src="https://github.com/user-attachments/assets/b57303aa-541a-402c-aac5-666ab84581f3" width="900" controls></video>  
   Tytuł Feature 1 -> Create -> karta w NEW.

3. **Edycja**  
   <video src="https://github.com/user-attachments/assets/6d0189a1-ef2e-4d35-9ce6-8ca4b45d5665" width="900" controls></video>  
   Edit -> zmiana tytułu -> Save.

4. **Przepływ statusów, anulowanie i filtry/taby**  
   <video src="https://github.com/user-attachments/assets/3a6cdded-6d82-4bb0-88c2-5f57ebacfd0e" width="900" controls></video>  
   Wideo przedstawia przepływ statusów (NEW -> IN PROGRESS -> DONE), anulowanie zadania (CANCELED) oraz użycie filtrów/tabów (NEW, IN PROGRESS, DONE, CANCELED, ALL).

---

## 3. Struktura projektu

Projekt jest zorganizowany w następujące katalogi, z których każdy pełni określoną funkcję:

```
app/
  api.py                # warstwa HTTP (Flask)
src/
  domain/              # modele domenowe + polityki uprawnień
  serwis/              # TaskService (logika aplikacji)
  repo/                # interfejsy + in-memory + Mongo
  integrations/        # emailer + stub SMTP (mockowane w unitach)
  utils/               # IdGenerator, Clock
tests/
  unit/                # testy jednostkowe (w tym integracje mockowane)
  api/                 # testy API (black-box, HTTP)
  bdd/                 # Behave: scenariusze Gherkin + kroki
  perf/                # testy wydajnościowe (HTTP)
.github/workflows/     # pipeline’y CI (unit/api/bdd/perf; in-memory i Mongo)
mongo.yml              # docker-compose dla MongoDB
requirements.txt
```

Szczegóły w README poszczególnych katalogów (`src/repo`, `tests/api`, `tests/bdd`, `tests/perf`, `src/integrations`, `tests/unit/...`).

---

## 4. Szybki start lokalnie

### In-memory

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

export PYTHONPATH=$PWD
export FLASK_APP="app.api:create_app"
flask run # http://127.0.0.1:5000
```

### MongoDB

```bash
docker compose -f mongo.yml up -d
export STORAGE=mongo
export MONGO_URI="mongodb://localhost:27017"
export MONGO_DB="taskmgr"

export PYTHONPATH=$PWD
python3 -m flask --app app.api:create_app run
```

### Frontend (Vite)

```bash
cd web && npm ci

# In-memory
npm run dev -- --host 127.0.0.1 --port 5173

# Mongo
VITE_API_URL=http://127.0.0.1:5000 npm run dev -- --host 127.0.0.1 --port 5173

# URL aplikacji
http://127.0.0.1:5173
```

---

## 5. API (skrót)

Wymagany nagłówek dla operacji na zadaniach: `X-Actor-Id: <user_id>`.

- **GET** `/health` -> `{ "status": "ok" }`
- **POST** `/api/users` → body: `{id, email, role, status}` (201)
- **POST** `/api/tasks` → `{title, description?, priority?}` (201)
- **PATCH** `/api/tasks/<id>` → aktualizacja wybranych pól (200)
- **DELETE** `/api/tasks/<id>` → miękki delete (200)
- **GET** `/api/tasks` → lista z filtrami `status`, `priority` (200)
- **POST** `/api/tasks/<id>/assign` → `{assignee_id}` (200)
- **POST** `/api/tasks/<id>/status` → `{status}` (200)
- **GET** `/api/tasks/<id>/events` → pełna historia (200)
- **POST** `/api/tasks/<id>/email-history` → `{email}` → `{ "sent": true }` (200, bez realnego SMTP)

**Przykład:**

```bash
curl -H "X-Actor-Id: u1" -H "Content-Type: application/json" \
 -d '{"title":"Feature X","priority":"HIGH"}' \
 http://127.0.0.1:5000/api/tasks
```

---

## 6. Testy i pokrycie

### Unit

```bash
python3 -m pytest tests/unit -q
python3 -m coverage run --source=src -m pytest tests/unit
python3 -m coverage report -m # pokrycie 100%
```

- **Mocki:** `SMTPClient.send`, `IdGenerator.new_id`, `Clock.now`.
- **Mongo:** testy mapowań + implementacji z „fakes” (bez prawdziwego serwera).

### API (black-box)

```bash
# serwer w drugim terminalu
python3 -m pytest tests/api -q
```

### BDD (Behave)

```bash
# serwer w drugim terminalu
python3 -m behave tests/bdd -q
```

### Performance

```bash
# serwer w drugim terminalu
# zmienne dostrajalne: BASE_URL, PERF_LIMIT (sekundy), PERF_N
python3 -m pytest tests/perf -q
```

### UI tests (Playwright)

```bash
cd web && npm ci && npx playwright install

npx playwright test

# Raport
npx playwright show-report
```

---

## 7. CI (GitHub Actions)

Workflowi odpalane na `push`/`pull_request` na `main`.  
Pliki w `.github/workflows/`:

- **`unit.yml`** — testy jednostkowe + coverage.
- **`api-inmemory.yml`** — API testy na in-memory.
- **`api-mongo.yml`** — API testy na Mongo.
- **`bdd-inmemory.yml` / `bdd-mongo.yml`** — scenariusze Behave.
- **`perf-inmemory.yml` / `perf-mongo.yml`** — smoke perf.
- **`ui-inmemory.yml`** — Vite + Playwright (in-memory).
- **`ui-mongo.yml`** — Vite + Playwright (Mongo).

UI-workflow buduje frontend, czeka na localhost:5173 i odpala Playwright, a raport jest publikowany jako artefakt.

---

## 8. Technologie użyte

- **Backend:** Flask, Python 3.10+
- **Frontend:** Vite, React, TypeScript
- **Baza danych:** MongoDB (produkcyjna), in-memory (testowa)
- **Testy:** Pytest, Behave, Playwright
- **CI/CD:** GitHub Actions

---

## 9. Dalsze prace

- **Frontend** (rejestracja użytkownika, UI zadań).
- **Rozszerzenie modelu User** o imię/nazwisko (API stabilne; zmiana w repo/mapowaniach i testach).
- **E-mail:** realna implementacja SMTP (obecnie stub + mock w unitach).

---

## 10. Wymagania wstępne

- **Python 3.10+**, `pip`, (opcjonalnie) Docker do MongoDB.
- **Instalacja:** `pip install -r requirements.txt`.

---

## 11. Gałęzie robocze i przepływ PR

Ocena dotyczy wyłącznie gałęzi `main`. Każda funkcjonalność powstaje w osobnej gałęzi -> PR -> merge do `main`. Poniżej konwencja oraz obecne gałęzie:

### Aktualne gałęzie

| Gałąź                 | Cel / zakres                                           | Powiązane workflowy CI                    |
| --------------------- | ------------------------------------------------------ | ----------------------------------------- |
| `feature/domain-core` | Modele domeny i polityki uprawnień                     | `unit-coverage`                           |
| `feature/api`         | Warstwa Flask (endpointy)                              | `api-inmemory`, `api-mongo`               |
| `feature/mongo`       | Repozytoria Mongo + mapowania                          | `api-mongo`, `bdd-mongo`, `unit-coverage` |
| `feature/bdd`         | Scenariusze Behave + kroki                             | `bdd-inmemory`, `bdd-mongo`               |
| `feature/performance` | Testy wydajności                                       | `perf-inmemory`, `perf-mongo`             |
| `feature/mock`        | Integracje zewnętrzne (SMTP/emailer) + unity z mockami | `unit-coverage`                           |
| `ci/unit-coverage`    | Konfiguracja i tuning coverage                         | `unit-coverage`                           |
| `ci/api-inmemory`     | Pipeline API (in-memory)                               | `api-inmemory`                            |
| `ci/api-mongo`        | Pipeline API (Mongo)                                   | `api-mongo`                               |
| `ci/bdd-inmemory`     | Pipeline BDD (in-memory)                               | `bdd-inmemory`                            |
| `ci/bdd-mongo`        | Pipeline BDD (Mongo)                                   | `bdd-mongo`                               |
| `ci/perf-inmemory`    | Pipeline performance (in-memory)                       | `perf-inmemory`                           |
| `ci/perf-mongo`       | Pipeline performance (Mongo)                           | `perf-mongo`                              |
| `ci/ui-inmemory`      | Pipeline UI (in-memory)                                | `ui-inmemory`                             |
| `ci/ui-mongo`         | Pipeline UI (Mongo)                                    | `ui-mongo`                                |

**Uwaga:** Workflowy są skonfigurowane na `on: push` do `main` oraz `on: pull_request -> main`.
