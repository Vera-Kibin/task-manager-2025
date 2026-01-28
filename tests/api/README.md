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

## Uwaga

Globalny handler 500 istnieje w aplikacji, ale nie jest testowany black-boxowo (brak specjalnego „awaryjnego” endpointu).
