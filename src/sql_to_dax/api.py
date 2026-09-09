from __future__ import annotations

from typing import Any

from sql_to_dax.dax import emit_dax
from sql_to_dax.diagnostics import TranslationReport
from sql_to_dax.errors import UnsupportedSqlError
from sql_to_dax.metadata import SemanticModel
from sql_to_dax.normalize import normalize
from sql_to_dax.parser import parse_one


def translate(
    sql: str,
    *,
    dialect: str = "databricks",
    metadata: SemanticModel | dict[str, Any] | None = None,
) -> str:
    """Translate a supported Databricks SparkSQL query into DAX."""
    if isinstance(metadata, SemanticModel):
        model = metadata
    else:
        model = SemanticModel.from_mapping(metadata)
    return emit_dax(normalize(parse_one(sql, dialect)), model)


def explain(
    sql: str,
    *,
    dialect: str = "databricks",
    metadata: SemanticModel | dict[str, Any] | None = None,
) -> TranslationReport:
    """Return a non-throwing report for a translation attempt."""
    try:
        dax = translate(sql, dialect=dialect, metadata=metadata)
        return TranslationReport(supported=True, dax=dax)
    except UnsupportedSqlError as exc:
        return TranslationReport(supported=False, diagnostic=exc.diagnostic)
