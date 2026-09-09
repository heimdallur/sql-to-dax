from __future__ import annotations

import argparse
import sys
from pathlib import Path

from sql_to_dax import __version__, translate
from sql_to_dax.errors import SqlToDaxError
from sql_to_dax.metadata import SemanticModel


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Translate Databricks SparkSQL into DAX.")
    parser.add_argument("sql_file", help="SQL file path, or '-' for stdin")
    parser.add_argument("--dialect", default="databricks", help="sqlglot input dialect")
    parser.add_argument("--metadata", type=Path, help="Optional TOML semantic metadata file")
    parser.add_argument("--version", action="version", version=f"sql-to-dax {__version__}")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.sql_file == "-":
        sql = sys.stdin.read()
    else:
        sql = Path(args.sql_file).read_text(encoding="utf-8")
    metadata = SemanticModel.from_toml(args.metadata) if args.metadata else None
    try:
        print(translate(sql, dialect=args.dialect, metadata=metadata))
    except SqlToDaxError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    return 0
