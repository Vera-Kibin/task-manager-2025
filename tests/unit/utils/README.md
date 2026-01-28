# Testy jednostkowe `utils` — `IdGenerator` i `Clock`

Zestaw minimalnych testów weryfikujących pomocnicze zależności używane przez serwis.

---

## Co testujemy

- **`IdGenerator.new_id()`**  
  Zwraca **różne** wartości przy kolejnych wywołaniach (unikalność identyfikatorów).

- **`Clock.now()`**  
  Zwraca obiekt zgodny z `datetime` (w teście sprawdzamy istnienie atrybutu `year`).

---

## Pliki testów

- `tests/unit/utils/test_utils.py`

---

## Uruchomienie

```bash
# tylko testy utils
python3 -m pytest tests/unit/utils -q

# z pomiarem pokrycia
python3 -m coverage run --source=src -m pytest tests/unit/utils
python3 -m coverage report -m
```

> Uwaga

Właściwe testy logiki biznesowej używają wersji deterministycznych (FakeIdGen, FakeClock).
Te testy w utils jedynie potwierdzają poprawność podstawowych implementacji.
