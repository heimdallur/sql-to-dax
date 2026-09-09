from __future__ import annotations

from typing import cast

import sqlglot
import sqlglot.expressions as exp


def parse_one(sql: str, dialect: str = "databricks") -> exp.Expression:
    """Parse a single SQL statement using sqlglot."""
    return cast(exp.Expression, sqlglot.parse_one(sql, read=dialect))
