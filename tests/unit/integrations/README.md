# Testy integracji — `tests/unit/integrations`

Zestaw testów jednostkowych demonstrujących mockowanie zewnętrznej integracji (SMTP) bez realnego I/O.

---

## Co tu jest

### `test_emailer.py`

Testuje `TaskHistoryEmailer.send_task_history(...)`:

- Mockowanie `SMTPClient.send` (sukces/porażka/wyjątek).
- Asercje parametrów wywołania (temat z dzisiejszą datą, treść z tytułem zadania i listą zdarzeń).
- Przypadek z pustą listą zdarzeń.

### `test_smtp_stub.py`

Weryfikuje stub `SMTPClient`:

- Zwraca `False`.
- Bez połączeń sieciowych.

---

## Dlaczego

- Spełnienie wymagania „zewnętrzna funkcjonalność, którą można mockować” (SMTP).
- Testy są szybkie i deterministyczne; brak zależności od realnego serwera poczty.

---

## Wymagania

- `pytest`
- `pytest-mock`

---

## Uruchomienie

```bash
python3 -m pytest tests/unit/integrations -q
```

---

## Uwaga

- API aplikacji nie korzysta z modułu e-mail; to odseparowana integracja pokazująca wzorzec DI + mock.
