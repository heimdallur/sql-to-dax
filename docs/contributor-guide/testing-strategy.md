# Testing Strategy

The project uses three layers of tests.

## 1. Unit Tests

Use focused tests for parser, normalizer, DAX emitter, diagnostics, metadata, and CLI behaviour.

## 2. Golden Fixtures

`tests/fixtures/supported.toml` contains exact SQL-to-DAX cases.

`tests/fixtures/unsupported.toml` contains SQL examples that must fail with stable diagnostic codes.

## 3. Quality Gates

Run before every pull request:

```bash
python -m ruff check .
python -m mypy src
python -m pytest --cov=sql_to_dax --cov-report=term-missing
python -m build
```

## Test Principle

Wrong DAX is worse than no DAX. Tests should prove refusal paths as carefully as successful translations.
