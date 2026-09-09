# Adding SQL Constructs

Every new SQL construct must move through the same path. Do not add string rewriting shortcuts.

## Required Workflow

1. Add or update a fixture in `tests/fixtures/supported.toml` or `tests/fixtures/unsupported.toml`.
2. Add focused unit tests when the fixture does not isolate the behaviour clearly.
3. Extend `src/sql_to_dax/logical.py` only if the construct needs a new semantic shape.
4. Extend `src/sql_to_dax/normalize.py` to map `sqlglot` AST nodes into the logical model.
5. Extend `src/sql_to_dax/dax.py` to emit deterministic DAX.
6. Update `docs/support-matrix.md`.
7. Run all quality gates.

## Acceptance Criteria

- Supported constructs must have exact SQL-to-DAX golden coverage.
- Unsupported constructs must raise `UnsupportedSqlError` with a stable diagnostic code.
- Semantically ambiguous constructs must remain unsupported until metadata can make them safe.

## Design Rule

If the only way to implement the feature is to inspect SQL strings directly, the design is probably wrong. Use the parsed AST and logical model.
