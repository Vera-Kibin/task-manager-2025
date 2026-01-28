# Testy jednostkowe domeny

Zbiór testów weryfikuje logikę domenową: modele (`User`, `Task`) oraz reguły uprawnień (`PermissionPolicy`). Testy są szybkie, deterministyczne i nie dotykają I/O ani zewnętrznych zależności.

---

## Jak uruchomić

```bash
python3 -m pytest tests/unit/domain -q

python3 -m coverage run --source=src -m pytest tests/unit/domain
python3 -m coverage report -m
```

---

## Wymagane pakiety

- `pytest`
- `coverage` (opcjonalnie, do raportu pokrycia)

---

## Pliki testowe i zakres

1. **test_policies.py** — PermissionPolicy

   Sprawdza reguły dostępu z `src/domain/policies.py`.

   Zakres:
   - can_create_task
     - użytkownik ACTIVE vs BLOCKED.
   - can_assign
     - MANAGER: może przypisać tylko aktywnego assignee,
     - USER: musi być właścicielem zadania i wskazać aktywnego assignee.
   - can_change_status
     - MANAGER może zawsze,
     - użytkownik BLOCKED nigdy,
     - przejście na DONE tylko przez aktualnego assignee,
     - inne statusy (NEW, IN_PROGRESS, CANCELED) może właściciel lub assignee; „obcy” nie może.
   - can_delete
     - MANAGER zawsze,
     - właściciel nie może usuwać zadań w statusie DONE.

   Techniki:
   - lekkie pomocniki \_u() i \_t() do czytelnego budowania danych testowych,
   - testy dodatnie i ujemne dla każdej gałęzi if/else.

---

2. **test_task_model.py** — Task

   Weryfikuje poprawność modelu Task z `src/domain/task.py`.

   Zakres:
   - wartości domyślne (status=NEW, priority=NORMAL, is_deleted=False),
   - walidacja tytułu (pusty, białe znaki, zbyt długi),
   - walidacja właściciela (owner_id niepusty),
   - walidacja typu daty (due_date musi być datetime lub None),
   - komunikaty wyjątków dla:
     - pustego id ("Task.id must be non-empty"),
     - nieprawidłowego priority ("priority must be Priority enum"),
     - nieprawidłowego status ("status must be TaskStatus enum").

   Techniki:
   - pytest.mark.parametrize do sprawdzenia wielu niepoprawnych wartości,
   - testy komunikatów błędów (czytelna diagnostyka przy regresji).

---

3. **test_user_model.py** — User

   Weryfikuje model User z `src/domain/user.py`.

   Zakres:
   - poprawna konstrukcja obiektu (id/email/role/status),
   - walidacja id (pusty/białe znaki/None -> wyjątek z komunikatem "User.id must be non-empty"),
   - walidacja email (kilka niepoprawnych wariantów -> "invalid email"),
   - typy pól enum:
     - role musi być Role,
     - status musi być Status (wymuszenie spójności typów).

   Techniki:
   - parametryzacja niepoprawnych e-maili,
   - jawne asercje treści komunikatów.

---

## Konwencje i dobre praktyki

- Testy domeny nie dotykają repozytoriów ani API — to czysta logika.
- Każdy test opisuje jedno zachowanie; nazwy testów są samowyjaśniające.
- W razie dodania pól/warunków w modelach/politykach — dopisz testy dodatnie i ujemne.
- Dążymy do wysokiego pokrycia linii i gałęzi (kluczowe if/else).

---

## Struktura

```
tests/
└── unit/
    └── domain/
        ├── test_policies.py
        ├── test_task_model.py
        └── test_user_model.py
src/
└── domain/
    ├── policies.py
    ├── task.py
    └── user.py
```
