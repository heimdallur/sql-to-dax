# Contributing

Contributions are welcome, but the project is intentionally conservative. The aim is trustworthy translation, not maximum syntax coverage.

## Rules for New SQL Support

Every new SQL construct must include:

1. A normalizer test proving the internal logical model.
2. A DAX emitter or API test proving exact output.
3. A supported or unsupported golden fixture.
4. Documentation in `docs/support-matrix.md`.
5. Stable diagnostic behavior for unsupported adjacent cases.

Do not add syntax support without proving the semantics are safe in DAX.

## Local Setup

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install -e '.[dev]'
```

## Checks

```bash
python -m ruff check .
python -m mypy src
python -m pytest --cov=sql_to_dax --cov-report=term-missing
python -m build
```

## Project Guides

- `docs/contributor-guide/adding-sql-constructs.md`
- `docs/contributor-guide/diagnostics.md`
- `docs/contributor-guide/testing-strategy.md`

## Dependency Policy

Runtime dependencies must be small, maintained, and necessary. Prefer the Python standard library where it is sufficient. New dependencies need a clear reason in the pull request.
