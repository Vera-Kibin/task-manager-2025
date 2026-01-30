# Warstwa HTTP aplikacji (Flask)

## Cel folderu

- Warstwa HTTP aplikacji opakowująca logikę `TaskService`.
- Fabryka aplikacji: `create_app()` w `app/api.py`.

---

## Struktura

- **`app/api.py`**  
  Definicje endpointów, rejestracja handlerów błędów, seeding użytkowników.
- **`app/__init__.py`**  
  Plik inicjalizujący moduł (pusty/techniczny).

---

## Uruchomienie lokalne

- **Wymagane**: Flask w `requirements.txt`.
- **Komendy**:
  ```bash
  export PYTHONPATH=$PWD
  export FLASK_APP="app.api:create_app"
  flask run # domyślnie port 5000
  ```
- **Health-check**:  
  `GET /health` → `{"status":"ok"}`.

---

## Wymagane nagłówki

- `X-Actor-Id: <user_id>` dla wszystkich operacji na zadaniach.

---

## Endpoints (skrót)

- **`POST /api/users`**  
  Tworzy użytkownika `{id,email,role?,status?}`.
- **`POST /api/tasks`**  
  Tworzy zadanie `{title,description?,priority?}`.
- **`PATCH /api/tasks/{id}`**  
  Aktualizacja `{title?,description?,priority?}`.
- **`POST /api/tasks/{id}/assign`**  
  `{assignee_id}`.
- **`POST /api/tasks/{id}/status`**  
  `{status}`.
- **`GET /api/tasks?status=&priority=`**  
  Lista widocznych zadań.
- **`DELETE /api/tasks/{id}`**  
  Miękkie usunięcie.
- **`GET /api/tasks/{id}/events`**  
  Historia zdarzeń.
- **`POST /api/tasks/{id}/email-history`**

---

## Format danych / Enums

- **Format**: JSON request/response.
- **Enums**:
  - `status`: `NEW`, `IN_PROGRESS`, `DONE`, `CANCELED`.
  - `priority`: `NORMAL`, `HIGH`.
  - `role`: `USER`, `MANAGER`; `user.status`: `ACTIVE`, `BLOCKED`.

---

## Błędy

- **400**: Walidacja (brak `X-Actor-Id`, zły enum, pusty tytuł).
- **403**: Brak uprawnień.
- **404**: Brak trasy.
- **500**: Globalny handler obecny (nie testowany black-boxowo).

---

## Storage

- Domyślnie in-memory (`InMemoryUsers/Tasks/Events`) osadzony w `create_app()`.
- _(Opcjonalnie na przyszłość)_ Przełącznik storage przez zmienne środowiskowe.

---

## Seeding

- `create_app()` dodaje przykładowych użytkowników: `m1` (MANAGER), `u1`, `u2`.

---

## Testy API (black-box)

- **Opis**: Serwer uruchomiony osobno; testy wysyłają HTTP do `BASE_URL` (domyślnie `http://127.0.0.1:5000`).
- **Uruchomienie**:
  ```bash
  python3 -m pytest tests/api
  ```
