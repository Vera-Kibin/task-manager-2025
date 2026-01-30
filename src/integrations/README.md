# Moduł e-mail (`src/integrations`)

Warstwa integracji z „zewnętrznym” światem. Moduł zawiera prosty adapter SMTP oraz klasę do wysyłania wiadomości e-mail z historią zadania. Funkcjonalność jest zaprojektowana tak, aby była łatwa do mockowania w testach jednostkowych.

---

## Pliki

### `smtp.py`

**`SMTPClient`**:  
Minimalny „stub” klienta SMTP. Zawiera metodę:

- **`send(subject: str, text: str, email_address: str) -> bool`**:
  - Realna wysyłka SMTP byłaby tutaj.
  - Zwraca `False` (brak realnego I/O).
  - W testach mockujemy metodę `send`.
  - **Adnotacja**: Metoda jest statyczna (`@staticmethod`).

### `emailer.py`

**`TaskHistoryEmailer`**:  
Klasa odpowiedzialna za składanie treści wiadomości e-mail i delegowanie wysyłki do `SMTPClient.send`.

- **`__init__(smtp: SMTPClient = None)`**:
  - Przyjmuje klienta SMTP (domyślnie `SMTPClient`).
- **`send_task_history(email: str, task_title: str, events: Sequence[str]) -> bool`**:
  - Składa temat i treść wiadomości (z datą i listą zdarzeń).
  - Deleguje wysyłkę do `SMTPClient.send`.

---

## Użycie (przykład)

```python
from src.integrations.emailer import TaskHistoryEmailer

ok = TaskHistoryEmailer().send_task_history(
    email="owner@example.com",
    task_title="Feature A",
    events=["CREATED", "ASSIGNED", "DONE"],
)
# ok == True/False w zależności od SMTPClient.send
```

W produkcji można wstrzyknąć własną implementację SMTP:

```python
real_smtp = MyRealSMTPClient()  # musi mieć metodę .send(subject, text, email) -> bool
ok = TaskHistoryEmailer(smtp=real_smtp).send_task_history("a@b.c", "T", [])
```

---

## Gdzie używane

Ten moduł nie jest wywoływany przez API; to opcjonalna integracja wykorzystywana w testach jednostkowych (mockowanie zewnętrznej usługi).

---

## Testowanie i mockowanie

### Testy jednostkowe

- **`tests/unit/integrations/test_emailer.py`**:
  - Mockowanie `SMTPClient.send`.
  - Asercje wywołań i treści wiadomości.
- **`tests/unit/integrations/test_smtp_stub.py`**:
  - Prosty test stuba (`SMTPClient`).
  - 100% pokrycia.

### Wymagania do testów

- `pytest`
- `pytest-mock`

### Uruchomienie testów

```bash
python3 -m pytest tests/unit/integrations -q
```

### Co mockujemy?

W testach `TaskHistoryEmailer` patchujemy `SMTPClient.send`, aby:

- Nie wykonywać realnej wysyłki.
- Sprawdzić parametry (`subject`, `body`, `email_address`).
- Zasymulować sukces/porażkę lub wyjątek.

## Dlaczego tak

- **Dependency Injection (DI)**:  
  `TaskHistoryEmailer` przyjmuje klienta SMTP w konstruktorze -> łatwo podmienić w testach/produkcji.
- **Brak I/O w unitach**:  
  Testy są szybkie i deterministyczne.
- **Spełnienie wymagania**:  
  Zewnętrzna funkcja (SMTP) jest mockowana w testach jednostkowych.
