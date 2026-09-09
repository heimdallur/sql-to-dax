# Semantic Model Metadata

DAX operates over a tabular semantic model. SQL text alone does not reliably tell the translator how tables, relationships, and measures should map.

`sql-to-dax` therefore supports optional TOML metadata for name mapping.

```toml
[tables.sales]
name = "Sales"

[tables.sales.columns]
region = "Region"
revenue = "Revenue"
```

## Current Scope

Metadata currently maps table and column names only.

## Future Scope

Relationship-aware joins and measure generation should use metadata rather than syntactic guessing.
