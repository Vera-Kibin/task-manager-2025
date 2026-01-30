# Testy jednostkowe serwisu — `TaskService`

Zestaw testów weryfikuje warstwę serwisu (`src/serwis/task_service.py`) w pełnej izolacji od I/O i zewnętrznych zasobów.

---

## Zakres

Sprawdzane są główne operacje serwisu:

- **`create_task`**  
  Walidacja danych, uprawnienia aktora, rejestracja zdarzenia `CREATED`.
- **`assign_task`**  
  Reguły przypisywania (właściciel/manager), blokady, metadane zdarzeń `ASSIGNED` (w tym poprzedni i nowy assignee).
- **`change_status`**  
  Dozwolone przejścia (`NEW → IN_PROGRESS → DONE/CANCELED`), uprawnienia (owner/assignee/manager), błędy i zdarzenia `STATUS_CHANGED`.
- **`update_task`**  
  Ograniczenia (brak zmian, DONE/CANCELED), walidacja pól, zdarzenia `UPDATED` z opisem zmian.
- **`delete_task`**  
  Miękkie usuwanie, idempotencja (brak drugiego `DELETED`), reguły owner/manager.
- **`list_tasks`**  
  Widoczność (user widzi swoje i przypisane, manager widzi wszystkie), filtry `status`/`priority`.
- **`get_events`**  
  Autoryzacja dostępu oraz pełna historia zdarzeń dla zadania.

Testy obejmują zarówno ścieżki „happy”, jak i przypadki błędne: `ValueError` dla walidacji/nieistniejących encji, `PermissionError` dla braku uprawnień, nieznane wartości enumów itp.

---

## Izolacja: dublowane zależności

Wszystkie testy używają in-memory/fake’ów zamiast realnych repozytoriów i zegara/ID:

- **Repozytoria**: używamy produkcyjnych implementacji in-memory z `src/repo/memory_repo.py` (`InMemoryUsers`, `InMemoryTasks`, `InMemoryEvents`).
- **FakeClock** i **FakeIdGen** zostały przeniesione do `helper.py` i są dostępne jako część fabryki `make_service()`.

Helper `tests/unit/serwis/helper.py` udostępnia fabrykę:

```python
svc, users, tasks, events = make_service()
```

Dzięki temu każdy test startuje ze świeżym, hermetycznym stanem.

---

## Struktura katalogu

- `fakes.py` — **(przeniesione)**: FakeClock i FakeIdGen są teraz w `helper.py`.
- `helper.py` — make_service() budujący TaskService z fake’ami.
- `test_create_assign.py` — tworzenie i przypisywanie zadań, przypadki zabronione, metadane ASSIGNED.
- `test_status.py` — przejścia statusów, reguły uprawnień, błędne przejścia i nieznane statusy.
- `test_update_delete.py` — aktualizacja pól (z walidacją i ograniczeniami), miękkie usuwanie i idempotencja DELETED.
- `test_list_events.py` — widoczność i filtrowanie w list_tasks, autoryzacja oraz kompletność historii zdarzeń.

---

## Uruchomienie

# tylko testy serwisu

python3 -m pytest tests/unit/serwis -q

# z pomiarem pokrycia (dla całego src/)

python3 -m coverage run --source=src -m pytest tests/unit
python3 -m coverage report -m

---

## Uwagi projektowe

- Testy serwisu nie importują warstwy HTTP/API i nie dotykają bazy — są to stricte unit-testy z mockowanymi/fake zależnościami.
- Dzięki deterministycznym FakeIdGen i FakeClock asercje na zdarzeniach (type, kolejność, metadane) są stabilne.
- Dodając nową metodę serwisu, dopisz test korzystający z make_service() i — jeśli potrzeba — uzupełnij fake’i o brakujące zachowania.

---

## Nowe testy: e-mail historii + deterministyczne ID/czas

1. **test_email_history.py**

Testuje metodę serwisową `TaskService.email_task_history(actor_id, task_id, email)` bez realnego I/O:

- **test_email_history_calls_smtp**  
  Patchuje `src.integrations.emailer.SMTPClient.send` i sprawdza:
  - że metoda została wywołana dokładnie raz,
  - parametry: temat zawiera `Task History`, adres to podany e-mail,
  - wynik `True` z mocka jest zwracany przez serwis.
- **test_email_history_missing_email_raises**  
  Pusta wartość e-mail → `ValueError("Missing email")`.
- **test_email_history_raises_notfound_when_task_missing**  
  Gdy `tasks.get(...)` zwróci `None` → `werkzeug.exceptions.NotFound`.  
  (W teście `get_events` jest spatchowane, aby nie dotykać reszty logiki).

Powiązane klasy/kod:  
`src/serwis/task_service.py::email_task_history`,  
`src/integrations/emailer.py`, `src/integrations/smtp.py`.

Uwaga: to spełnia wymaganie „zewnętrzna funkcjonalność, którą można mockować” (SMTP).  
W testach używamy `pytest-mock` do patchowania wywołania SMTP.

2. **test_idgen_clock_mock.py**

Stabilizuje identyfikatory i czas zdarzeń przez mocki:

- **test_create_task_uses_mocked_id_and_clock**  
  Patchuje:
  - `src.utils.idgen.IdGenerator.new_id` → stały `"fixed-id-123"`,
  - `src.utils.clock.Clock.now` → ustalona data/czas.  
    Asercje: `Task.id` oraz `TaskEvent.CREATED.timestamp` dokładnie równe wartościom z mocków.
- **test_status_change_event_uses_mocked_clock**  
  Tworzy task przy stałym „teraz”, następnie patchuje kolejny „teraz” i sprawdza, że `STATUS_CHANGED.timestamp` to druga, spatchowana wartość.

**Dlaczego:**  
Deterministyczne wartości (ID/czas) dają powtarzalne testy i precyzyjne asercje na historii zdarzeń.

---

### Szybkie uruchomienie tylko tych plików

```bash
python3 -m pytest tests/unit/serwis/test_email_history.py -q
python3 -m pytest tests/unit/serwis/test_idgen_clock_mock.py -q
```

**Wymagane:** `pytest`, `pytest-mock`.
