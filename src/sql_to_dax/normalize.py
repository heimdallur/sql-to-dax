from __future__ import annotations

from typing import Literal, cast

import sqlglot.expressions as exp

from sql_to_dax.errors import UnsupportedSqlError
from sql_to_dax.logical import (
    Aggregate,
    ColumnRef,
    LiteralValue,
    LogicalQuery,
    OrderBy,
    Predicate,
    Projection,
)


def normalize(expression: exp.Expression) -> LogicalQuery:
    _reject_unsupported(expression)
    if not isinstance(expression, exp.Select):
        raise UnsupportedSqlError("unsupported.statement", "Only SELECT statements are supported")

    from_arg = expression.args.get("from") or expression.args.get("from_")
    if from_arg is None or not isinstance(from_arg.this, exp.Table):
        raise UnsupportedSqlError(
            "unsupported.from",
            "Only single-table FROM clauses are supported",
        )
    source_table = from_arg.this.name

    filters = None
    where = expression.args.get("where")
    if isinstance(where, exp.Where):
        filters = _predicate(where.this, source_table)

    group_by = _group_by(expression, source_table)
    projections = [_projection(item, source_table) for item in expression.expressions]
    _validate_grouping(projections, group_by)

    return LogicalQuery(
        source_table=source_table,
        projections=projections,
        filters=filters,
        group_by=group_by,
        order_by=_order_by(expression, source_table),
        limit=_limit(expression),
    )


def _reject_unsupported(expression: exp.Expression) -> None:
    if expression.find(exp.Join):
        raise UnsupportedSqlError("unsupported.join", "JOIN is not supported yet")
    for star in expression.find_all(exp.Star):
        if not isinstance(star.parent, exp.Count):
            raise UnsupportedSqlError("unsupported.star", "SELECT * is not supported")
    if expression.args.get("with") or expression.args.get("with_") or expression.find(exp.CTE):
        raise UnsupportedSqlError("unsupported.cte", "CTEs are not supported yet")
    if expression.find(exp.Window):
        raise UnsupportedSqlError("unsupported.window", "Window functions are not supported")
    if expression.args.get("having"):
        raise UnsupportedSqlError("unsupported.having", "HAVING is not supported yet")


def _projection(node: exp.Expression, source_table: str) -> Projection:
    alias = node.alias if isinstance(node, exp.Alias) else None
    inner = node.this if isinstance(node, exp.Alias) else node
    if isinstance(inner, exp.Column):
        return Projection(_column(inner, source_table), alias=alias)
    aggregate = _aggregate(inner, source_table)
    if aggregate:
        return Projection(aggregate, alias=alias or _default_aggregate_alias(aggregate))
    raise UnsupportedSqlError("unsupported.projection", f"Unsupported projection: {inner}")


def _aggregate(node: exp.Expression, source_table: str) -> Aggregate | None:
    funcs: dict[type[exp.Expression], str] = {
        exp.Sum: "SUM",
        exp.Avg: "AVG",
        exp.Min: "MIN",
        exp.Max: "MAX",
        exp.Count: "COUNT",
    }
    func = funcs.get(type(node))
    if func is None:
        return None
    if isinstance(node, exp.Count) and isinstance(node.this, exp.Star):
        return Aggregate("COUNT", None)
    if not isinstance(node.this, exp.Column):
        raise UnsupportedSqlError(
            "unsupported.aggregate",
            f"Unsupported aggregate argument: {node}",
        )
    return Aggregate(func, _column(node.this, source_table))  # type: ignore[arg-type]


def _default_aggregate_alias(aggregate: Aggregate) -> str:
    if aggregate.argument is None:
        return "count"
    return f"{aggregate.function.lower()}_{aggregate.argument.name}"


def _group_by(expression: exp.Expression, source_table: str) -> list[ColumnRef]:
    group = expression.args.get("group")
    if group is None:
        return []
    return [_column(item, source_table) for item in group.expressions]


def _validate_grouping(projections: list[Projection], group_by: list[ColumnRef]) -> None:
    has_aggregate = any(isinstance(projection.expression, Aggregate) for projection in projections)
    if not has_aggregate:
        return
    grouped = {(column.table, column.name) for column in group_by}
    for projection in projections:
        expression = projection.expression
        if isinstance(expression, ColumnRef) and (expression.table, expression.name) not in grouped:
            raise UnsupportedSqlError(
                "unsupported.semantic.ungrouped_column",
                f"Column {expression.name!r} must appear in GROUP BY",
            )


def _order_by(expression: exp.Expression, source_table: str) -> list[OrderBy]:
    order = expression.args.get("order")
    if order is None:
        return []
    items: list[OrderBy] = []
    for ordered in order.expressions:
        direction: Literal["ASC", "DESC"] = "DESC" if ordered.args.get("desc") else "ASC"
        target = ordered.this
        if isinstance(target, exp.Column):
            name = target.name
            if target.table:
                items.append(OrderBy(_column(target, source_table), direction))
            else:
                items.append(OrderBy(name, direction))
        else:
            raise UnsupportedSqlError(
                "unsupported.order",
                f"Unsupported ORDER BY expression: {target}",
            )
    return items


def _limit(expression: exp.Expression) -> int | None:
    limit = expression.args.get("limit")
    if limit is None:
        return None
    node = limit.expression
    if isinstance(node, exp.Literal) and not node.is_string:
        return int(node.this)
    raise UnsupportedSqlError("unsupported.limit", f"Unsupported LIMIT value: {limit}")


def _predicate(node: exp.Expression, source_table: str) -> Predicate:
    if isinstance(node, exp.Paren):
        return _predicate(cast(exp.Expression, node.this), source_table)
    if isinstance(node, exp.And):
        return Predicate(
            "AND",
            _predicate(cast(exp.Expression, node.left), source_table),
            _predicate(cast(exp.Expression, node.right), source_table),
        )
    if isinstance(node, exp.Or):
        return Predicate(
            "OR",
            _predicate(cast(exp.Expression, node.left), source_table),
            _predicate(cast(exp.Expression, node.right), source_table),
        )
    binary: dict[type[exp.Expression], str] = {
        exp.EQ: "=",
        exp.NEQ: "<>",
        exp.GT: ">",
        exp.GTE: ">=",
        exp.LT: "<",
        exp.LTE: "<=",
    }
    op = binary.get(type(node))
    if op:
        binary_node = cast(exp.Binary, node)
        return Predicate(
            op,
            _column(cast(exp.Expression, binary_node.left), source_table),
            _literal(cast(exp.Expression, binary_node.right)),
        )
    if isinstance(node, exp.In):
        values = [_literal(item) for item in node.expressions]
        return Predicate("IN", _column(node.this, source_table), values)
    if isinstance(node, exp.Not) and isinstance(node.this, exp.Is):
        inner = node.this
        if isinstance(inner.expression, exp.Null):
            return Predicate("IS NOT NULL", _column(inner.this, source_table), None)
    if isinstance(node, exp.Is):
        right = node.expression
        if isinstance(right, exp.Null):
            return Predicate("IS NULL", _column(node.this, source_table), None)
    raise UnsupportedSqlError("unsupported.predicate", f"Unsupported predicate: {node}")


def _column(node: exp.Expression, source_table: str) -> ColumnRef:
    if not isinstance(node, exp.Column):
        raise UnsupportedSqlError("unsupported.column", f"Unsupported column reference: {node}")
    return ColumnRef(name=node.name, table=node.table or source_table)


def _literal(node: exp.Expression) -> LiteralValue:
    if isinstance(node, exp.Null):
        return LiteralValue(None)
    if isinstance(node, exp.Boolean):
        return LiteralValue(bool(node.this))
    if isinstance(node, exp.Literal):
        if node.is_string:
            return LiteralValue(str(node.this))
        text = str(node.this)
        return LiteralValue(float(text) if "." in text else int(text))
    raise UnsupportedSqlError("unsupported.literal", f"Unsupported literal: {node}")
