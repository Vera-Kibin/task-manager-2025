# BDD tests (`tests/bdd`)

Zestaw testów BDD (Behave) uruchamianych black-box przez HTTP wobec warstwy Flask.

---

## Struktura

- **`features/task_flow.feature`**:  
  Scenariusze (health, widoczność zadań, update + soft-delete, assign, zmiany statusu, walidacje).
- **`steps/task_steps.py`**:  
  Implementacje kroków (HTTP przez `requests`).

---

## Wymagania

- `behave`
- `requests`

---

## Uruchomienie lokalne (in-memory)

```bash
export PYTHONPATH=$PWD
export FLASK_APP="app.api:create_app"
python3 -m flask run &           # http://127.0.0.1:5000
python3 -m behave tests/bdd -q
```

---

## Uruchomienie lokalne (Mongo)

```bash
docker compose -f mongo.yml up -d
export STORAGE=mongo
export MONGO_URI="mongodb://localhost:27017"
export MONGO_DB="taskmgr"
export PYTHONPATH=$PWD
python3 -m flask --app app.api:create_app run &
python3 -m behave tests/bdd -q
```

---

## Konfiguracja adresu API

Domyślnie `BASE_URL=http://127.0.0.1:5000`. Można nadpisać:

```bash
export BASE_URL="http://127.0.0.1:5001"
python3 -m behave tests/bdd -q
```

---

## Uruchomienie wybranych testów

- **Konkretny plik**:
  ```bash
  python3 -m behave tests/bdd/features/task_flow.feature -q
  ```
- **Konkretny scenariusz po nazwie**:
  ```bash
  python3 -m behave tests/bdd/features/task_flow.feature -n "Owner sees only own tasks" -q
  ```

---

## Uwagi

- Testy nie importują kodu aplikacji; komunikacja wyłącznie przez HTTP.
- Kroki „Task list for actor … is empty” czyszczą stan tylko dla wskazanego aktora, bez resetu bazy.
