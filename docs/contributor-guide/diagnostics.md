# Diagnostics

Diagnostics are part of the public contributor contract. They explain why translation failed and where contributors can improve support.

## Shape

```python
Diagnostic(
    code="unsupported.join",
    message="JOIN is not supported yet",
    hint="Relationship metadata is required before joins can be translated safely.",
    docs_url="https://github.com/heimdallur/sql-to-dax/blob/main/docs/support-matrix.md#joins",
)
```

## Code Rules

- Codes are stable. Do not rename them casually.
- Use `unsupported.<construct>` for unsupported syntax.
- Use `unsupported.semantic.<reason>` for unsafe semantics.
- Messages should be short and specific.
- Hints should tell the user what is needed, not hand-wave.

## Examples

- `unsupported.join`
- `unsupported.cte`
- `unsupported.window`
- `unsupported.having`
- `unsupported.semantic.ungrouped_column`
