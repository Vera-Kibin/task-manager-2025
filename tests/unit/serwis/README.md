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

- `InMemoryUsers`, `InMemoryTasks`, `InMemoryEvents` — proste pamięciowe implementacje interfejsów repozytoriów.
- `FakeIdGen` — deterministyczny generator (`id-1`, `id-2`, …).
- `FakeClock` — deterministyczny czas; każde `now()` zwiększa się o sekundę (ułatwia porządkowanie zdarzeń po `timestamp`).

Helper `tests/unit/serwis/helper.py` udostępnia fabrykę:

```python
svc, users, tasks, events = make_service()
```

Dzięki temu każdy test startuje ze świeżym, hermetycznym stanem.

---

## Struktura katalogu

- `fakes.py` — implementacje InMemory\*, FakeIdGen, FakeClock.
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

python3 -m coverage run --source=src -m pytest tests/unit/serwis
python3 -m coverage report -m

---

## Uwagi projektowe

- Testy serwisu nie importują warstwy HTTP/API i nie dotykają bazy — są to stricte unit-testy z mockowanymi/fake zależnościami.
- Dzięki deterministycznym FakeIdGen i FakeClock asercje na zdarzeniach (type, kolejność, metadane) są stabilne.
- Dodając nową metodę serwisu, dopisz test korzystający z make_service() i — jeśli potrzeba — uzupełnij fake’i o brakujące zachowania.
