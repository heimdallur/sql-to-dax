from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import Literal, TypeAlias


@dataclass(frozen=True)
class ColumnRef:
    name: str
    table: str | None = None


@dataclass(frozen=True)
class LiteralValue:
    value: str | int | float | bool | None


@dataclass(frozen=True)
class Predicate:
    operator: str
    left: Expression | Predicate
    right: Expression | Predicate | Sequence[Expression] | None = None


@dataclass(frozen=True)
class Aggregate:
    function: Literal["COUNT", "SUM", "AVG", "MIN", "MAX"]
    argument: ColumnRef | None = None


Expression: TypeAlias = ColumnRef | LiteralValue | Aggregate


@dataclass(frozen=True)
class Projection:
    expression: Expression
    alias: str | None = None


@dataclass(frozen=True)
class OrderBy:
    expression: ColumnRef | str
    direction: Literal["ASC", "DESC"] = "ASC"


@dataclass(frozen=True)
class LogicalQuery:
    source_table: str
    projections: list[Projection] = field(default_factory=list)
    filters: Predicate | None = None
    group_by: list[ColumnRef] = field(default_factory=list)
    order_by: list[OrderBy] = field(default_factory=list)
    limit: int | None = None
