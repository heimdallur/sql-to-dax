from __future__ import annotations

import tomllib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class TableMetadata:
    name: str | None = None
    columns: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class SemanticModel:
    tables: dict[str, TableMetadata] = field(default_factory=dict)

    @classmethod
    def from_mapping(cls, data: dict[str, Any] | None) -> SemanticModel:
        if not data:
            return cls()
        tables: dict[str, TableMetadata] = {}
        for source_name, raw_table in data.get("tables", {}).items():
            if not isinstance(raw_table, dict):
                continue
            raw_columns = raw_table.get("columns", {})
            if isinstance(raw_columns, dict):
                columns = {str(k): str(v) for k, v in raw_columns.items()}
            else:
                columns = {}
            name = raw_table.get("name")
            tables[str(source_name)] = TableMetadata(
                name=str(name) if name else None,
                columns=columns,
            )
        return cls(tables=tables)

    @classmethod
    def from_toml(cls, path: str | Path) -> SemanticModel:
        raw = Path(path).read_text(encoding="utf-8")
        return cls.from_mapping(tomllib.loads(raw))

    def table_name(self, table: str) -> str:
        metadata = self.tables.get(table)
        return metadata.name if metadata and metadata.name else table

    def column_name(self, table: str, column: str) -> str:
        metadata = self.tables.get(table)
        if metadata is None:
            return column
        return metadata.columns.get(column, column)
