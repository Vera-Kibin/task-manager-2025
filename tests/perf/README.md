# Testy wydajności — `tests/perf`

Lekki, czarnoskrzynkowy pomiar czasu odpowiedzi HTTP dla kluczowych ścieżek API. Testy nie mierzą przepustowości całego systemu; sprawdzają, czy pojedyncze requesty mieszczą się w zdefiniowanym limicie czasu.

---

## Co mierzymy

- **Tworzenie wielu zadań, ich listowanie i soft-delete**  
  (`test_perf_create_list_delete_many_tasks`).
- **Przepływ „assign → IN_PROGRESS → DONE” w pętli**  
  (`test_perf_assign_and_status_flow`).

Każdy request jest asercją porównywany z limitem `PERF_LIMIT` na podstawie `response.elapsed`.

---

## Parametry (zmienne środowiskowe)

- **`BASE_URL`** — adres API (domyślnie `http://127.0.0.1:5000`).
- **`PERF_LIMIT`** — maksymalny czas pojedynczego requestu w sekundach (domyślnie `0.5`).
- **`PERF_N`** — liczba iteracji (domyślnie `60`).

**Przykład:**

```bash
export BASE_URL="http://127.0.0.1:5000"
export PERF_LIMIT=0.6
export PERF_N=80
```

---

## Uruchomienie lokalne

### In-memory

```bash
export PYTHONPATH=$PWD
export FLASK_APP="app.api:create_app"
flask run & # http://127.0.0.1:5000
python3 -m pytest tests/perf -q
```

### Mongo

```bash
docker compose -f mongo.yml up -d
export STORAGE=mongo
export MONGO_URI="mongodb://localhost:27017"
export MONGO_DB="taskmgr"
export PYTHONPATH=$PWD
python3 -m flask --app app.api:create_app run & # http://127.0.0.1:5000
python3 -m pytest tests/perf -q
```

---

## Założenia i skróty

- Testy są black-box (HTTP przez `requests`), z reuse połączeń via `requests.Session`.
- **Idempotencja**: testy używają unikalnych ID (`uuid`) i czyszczą stan właściciela (soft-delete).
- To nie jest test obciążeniowy (brak równoległości); celem jest regresyjne SLA na pojedynczy request.

---

## Integracja z CI

W repo są dwa workflowy:

- `.github/workflows/perf-inmemory.yml` — in-memory (szybszy limit, większe `PERF_N`).
- `.github/workflows/perf-mongo.yml` — Mongo (luźniejszy limit, mniejsze `PERF_N`).
