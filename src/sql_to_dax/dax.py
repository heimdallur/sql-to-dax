from __future__ import annotations

from sql_to_dax.errors import UnsupportedSqlError
from sql_to_dax.logical import Aggregate, ColumnRef, LiteralValue, LogicalQuery, OrderBy, Predicate
from sql_to_dax.metadata import SemanticModel


def emit_dax(query: LogicalQuery, metadata: SemanticModel | None = None) -> str:
    model = metadata or SemanticModel()
    table_expr = _table_expression(query, model)
    if query.limit is not None:
        table_expr = _topn(query, table_expr, model)
    result = f"EVALUATE\n{table_expr}"
    if query.limit is None and query.order_by:
        order_parts = ", ".join(_order_expression(item, query, model) for item in query.order_by)
        result = f"{result}\nORDER BY {order_parts}"
    return result


def _table_expression(query: LogicalQuery, model: SemanticModel) -> str:
    has_aggregate = any(
        isinstance(projection.expression, Aggregate) for projection in query.projections
    )
    if query.group_by or has_aggregate:
        return _summarizecolumns(query, model)
    return _selectcolumns(query, model)


def _selectcolumns(query: LogicalQuery, model: SemanticModel) -> str:
    source = _filter_source(query, model)
    parts = []
    for projection in query.projections:
        if not isinstance(projection.expression, ColumnRef):
            raise UnsupportedSqlError(
                "unsupported.emit",
                "Only column projections are valid in SELECTCOLUMNS",
            )
        table = projection.expression.table or query.source_table
        label = projection.alias or model.column_name(table, projection.expression.name)
        parts.append(f'{_string(label)}, {_column(projection.expression, model)}')
    return f"SELECTCOLUMNS({source}, {', '.join(parts)})"


def _summarizecolumns(query: LogicalQuery, model: SemanticModel) -> str:
    parts = [_column(column, model) for column in query.group_by]
    if query.filters is not None:
        table = _table(query.source_table, model)
        parts.append(f"FILTER({table}, {_predicate(query.filters, model)})")
    for projection in query.projections:
        if isinstance(projection.expression, Aggregate):
            alias = projection.alias or _aggregate_alias(projection.expression)
            aggregate = _aggregate(projection.expression, query.source_table, model)
            parts.append(f"{_string(alias)}, {aggregate}")
    return f"SUMMARIZECOLUMNS({', '.join(parts)})"


def _filter_source(query: LogicalQuery, model: SemanticModel) -> str:
    table = _table(query.source_table, model)
    if query.filters is None:
        return table
    return f"FILTER({table}, {_predicate(query.filters, model)})"


def _topn(query: LogicalQuery, table_expr: str, model: SemanticModel) -> str:
    if query.limit is None:
        raise AssertionError("limit is required")
    order = query.order_by[0] if query.order_by else None
    if order is None:
        return f"TOPN({query.limit}, {table_expr})"
    order_expr = _order_expression(order, query, model)
    return f"TOPN({query.limit}, {table_expr}, {order_expr})"


def _order_expression(order: OrderBy, query: LogicalQuery, model: SemanticModel) -> str:
    expr = order.expression
    if isinstance(expr, ColumnRef):
        target = _column(expr, model)
    elif _is_projection_alias(expr, query):
        target = f"[{expr}]"
    else:
        target = _column(ColumnRef(name=expr, table=query.source_table), model)
    if query.limit is not None:
        return f"{target}, {order.direction}"
    return f"{target} {order.direction}"


def _is_projection_alias(value: str, query: LogicalQuery) -> bool:
    return any(projection.alias == value for projection in query.projections)


def _aggregate(aggregate: Aggregate, source_table: str, model: SemanticModel) -> str:
    if aggregate.function == "COUNT" and aggregate.argument is None:
        return f"COUNTROWS({_table(source_table, model)})"
    if aggregate.argument is None:
        raise UnsupportedSqlError(
            "unsupported.aggregate",
            f"{aggregate.function} requires a column",
        )
    return f"{aggregate.function}({_column(aggregate.argument, model)})"


def _aggregate_alias(aggregate: Aggregate) -> str:
    if aggregate.argument is None:
        return "count"
    return f"{aggregate.function.lower()}_{aggregate.argument.name}"


def _predicate(predicate: Predicate, model: SemanticModel) -> str:
    if (
        predicate.operator in {"AND", "OR"}
        and isinstance(predicate.left, Predicate)
        and isinstance(predicate.right, Predicate)
    ):
        left = _predicate(predicate.left, model)
        right = _predicate(predicate.right, model)
        return f"({left} {predicate.operator} {right})"
    if (
        predicate.operator == "IN"
        and isinstance(predicate.left, ColumnRef)
        and isinstance(predicate.right, list | tuple)
    ):
        values = ", ".join(
            _literal(item.value) for item in predicate.right if isinstance(item, LiteralValue)
        )
        return f"{_column(predicate.left, model)} IN {{{values}}}"
    if predicate.operator == "IS NULL" and isinstance(predicate.left, ColumnRef):
        return f"ISBLANK({_column(predicate.left, model)})"
    if predicate.operator == "IS NOT NULL" and isinstance(predicate.left, ColumnRef):
        return f"NOT ISBLANK({_column(predicate.left, model)})"
    if isinstance(predicate.left, ColumnRef) and isinstance(predicate.right, LiteralValue):
        left = _column(predicate.left, model)
        right = _literal(predicate.right.value)
        return f"{left} {predicate.operator} {right}"
    raise UnsupportedSqlError("unsupported.predicate", "Unsupported predicate shape")


def _table(source_table: str, model: SemanticModel) -> str:
    return _quote_table(model.table_name(source_table))


def _column(column: ColumnRef, model: SemanticModel) -> str:
    table = column.table or ""
    dax_table = model.table_name(table)
    dax_column = model.column_name(table, column.name)
    return f"{_quote_table(dax_table)}[{dax_column}]"


def _quote_table(name: str) -> str:
    return "'" + name.replace("'", "''") + "'"


def _string(value: str) -> str:
    return '"' + value.replace('"', '""') + '"'


def _literal(value: object) -> str:
    if value is None:
        return "BLANK()"
    if isinstance(value, bool):
        return "TRUE()" if value else "FALSE()"
    if isinstance(value, str):
        return _string(value)
    return str(value)
