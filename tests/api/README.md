# Testy API — `tests/api/test_tasks_api.py`

Krótki zestaw black-box testów HTTP dla warstwy Flask. Testy nie importują kodu aplikacji — komunikują się wyłącznie przez REST.

---

## Zakres

Pokryte endpointy i przypadki:

- **Health**:  
  `GET /health`.
- **Users**:  
  `POST /api/users` (201, brak pola -> 400).
- **Tasks CRUD**:  
  `POST /api/tasks`, `GET /api/tasks`, `PATCH /api/tasks/{id}`, `DELETE /api/tasks/{id}`
  - Widoczność dla ownera, ukrycie po soft-delete.
  - Walidacje: pusty tytuł (400), nieznany `priority` (400), brak `X-Actor-Id` (400).
- **Assign/Status/Events**:  
  `POST /api/tasks/{id}/assign`, `POST /api/tasks/{id}/status`, `GET /api/tasks/{id}/events`
  - Szczęśliwe ścieżki i błędy: 403 (brak uprawnień), 400 (nieznany status, nielegalna zmiana stanu, brak pola).
- **Filtrowanie**:  
  `GET /api/tasks?status=&priority=`.
- **404**:  
  Nieistniejąca trasa zwraca 404.

---

## Założenia testów

- Serwer działa pod `BASE_URL` (domyślnie `http://127.0.0.1:5000`).  
  Można nadpisać:
  ```bash
  export BASE_URL="http://127.0.0.1:5000"
  ```
- Wszystkie operacje na zadaniach wymagają nagłówka:  
  `X-Actor-Id: <user_id>`.
- Testy tworzą użytkowników i zadania dynamicznie (unikalne ID przez `uuid`), więc są niezależne od kolejności i idempotentne.

---

## Szybkie uruchomienie

1. **Uruchom API** (w innym terminalu):

   ```bash
   export PYTHONPATH=$PWD
   export FLASK_APP="app.api:create_app"
   flask run
   ```

2. **Odpal testy**:

   ```bash
   python3 -m pytest tests/api -q
   ```

---

## Struktura pliku

- **Helpery**:  
  `H()` (nagłówki), `new_id()` (unikalne ID), `create_user()`, `create_task()`.
- **Zgrupowane testy**:
  - `sanity/health`
  - `CRUD`
  - `assign/status/events`
  - `filtrowanie`
  - `walidacje/błędy`.

---

## Dodatkowy scenariusz: wysyłka historii e-mailem

**Test**: `tests/api/test_tasks_api.py::test_email_history_happy_path_returns_sent_true`

### Co sprawdza

- Black-box `POST /api/tasks/{id}/email-history` z body `{"email": "a@b.c"}`.
- Nagłówek `X-Actor-Id` jest wymagany (aktor = owner zadania).
- Oczekuje `200` i body `{"sent": true}`.

### Wymagane po stronie API

- **Endpoint**:

  ```http
  POST /api/tasks/<task_id>/email-history
  Headers: X-Actor-Id: <user_id>
  Body: {"email": "<addr>"}
  Response: 200 {"sent": true}
  ```

- **Handler** może zwracać `{"sent": true}` bez realnego SMTP (test API nie mockuje I/O; logika SMTP jest w unitach).

### Minimalne helpery używane w teście

```python
import os, uuid, requests
BASE = os.getenv("BASE_URL", "http://127.0.0.1:5000")

def H(actor_id: str) -> dict:
    return {"Content-Type": "application/json", "X-Actor-Id": actor_id}

def new_id(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex[:8]}"

def create_user(user_id: str, role: str = "USER", status: str = "ACTIVE") -> None:
    r = requests.post(f"{BASE}/api/users", json={"id": user_id, "email": f"{user_id}@ex.com", "role": role, "status": status}, timeout=5)
    assert r.status_code == 201, r.text

def create_task(actor_id: str, title: str = "T") -> dict:
    r = requests.post(f"{BASE}/api/tasks", headers=H(actor_id), json={"title": title}, timeout=5)
    assert r.status_code == 201, r.text
    return r.json()
```

### Przykładowy test

```python
def test_email_history_happy_path_returns_sent_true():
    owner = new_id("owner")
    create_user(owner)
    t = create_task(owner, "Feature-X")

    r = requests.post(
        f"{BASE}/api/tasks/{t['id']}/email-history",
        headers=H(owner),
        json={"email": "a@b.c"},
        timeout=5,
    )
    assert r.status_code == 200
    assert r.json() == {"sent": True}
```

### Uruchomienie (in-memory)

```bash
export PYTHONPATH=$PWD
export FLASK_APP="app.api:create_app"
flask run &
python3 -m pytest tests/api -q
```

### Uruchomienie (Mongo)

```bash
docker compose -f mongo.yml up -d
export STORAGE=mongo
export MONGO_URI="mongodb://localhost:27017"
export MONGO_DB="taskmgr"
export PYTHONPATH=$PWD
python3 -m flask --app app.api:create_app run &
python3 -m pytest tests/api -q
```

### Uwaga

- Ten test nie mockuje SMTP na poziomie API — zakłada, że endpoint zwraca `{"sent": true}` (bez realnej wysyłki).
- Mockowanie i asercje parametrów wysyłki są pokryte w testach unit modułu `src/integrations` oraz `TaskService.email_task_history(...)`.

---

## Uwaga

Globalny handler 500 istnieje w aplikacji, ale nie jest testowany black-boxowo (brak specjalnego „awaryjnego” endpointu).
