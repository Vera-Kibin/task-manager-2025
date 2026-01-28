# Utils

Zestaw drobnych narzędzi izolujących losowość i czas od logiki aplikacji — łatwe do mockowania w testach.

---

## Moduły

- **idgen.py**
  - `IdGenerator.new_id() -> str` – zwraca unikalny identyfikator (UUID v4 w postaci stringa).
- **clock.py**
  - `Clock.now() -> datetime` – zwraca bieżącą datę i czas (`datetime.now()`).

---

## Użycie

```python
from src.utils.idgen import IdGenerator
from src.utils.clock import Clock

task_id = IdGenerator.new_id()
timestamp = Clock.now()
```

---

## Testy (mock)

- Narzędzia są łatwe do mockowania w testach, co pozwala na kontrolowanie losowości i czasu w aplikacji.

```python
def test_with_fixed_time_and_id(monkeypatch):
    monkeypatch.setattr("src.utils.idgen.IdGenerator.new_id", lambda: "fixed-id")
    from datetime import datetime
    monkeypatch.setattr("src.utils.clock.Clock.now", lambda: datetime(2025,1,1,12,0,0))
```
