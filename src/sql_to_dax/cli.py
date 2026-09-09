from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from sql_to_dax import __version__, explain, translate
from sql_to_dax.errors import SqlToDaxError
from sql_to_dax.metadata import SemanticModel


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Translate Databricks SparkSQL into DAX.")
    parser.add_argument("command_or_file", help="SQL file path, '-', or 'explain'")
    parser.add_argument("sql_file", nargs="?", help="SQL file path when using 'explain'")
    parser.add_argument("--dialect", default="databricks", help="sqlglot input dialect")
    parser.add_argument("--metadata", type=Path, help="Optional TOML semantic metadata file")
    parser.add_argument("--version", action="version", version=f"sql-to-dax {__version__}")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    metadata = SemanticModel.from_toml(args.metadata) if args.metadata else None
    if args.command_or_file == "explain":
        if args.sql_file is None:
            parser.error("explain requires a SQL file path or '-'")
        return _explain_command(args.sql_file, args.dialect, metadata)
    return _translate_command(args.command_or_file, args.dialect, metadata)


def _translate_command(sql_file: str, dialect: str, metadata: SemanticModel | None) -> int:
    try:
        print(translate(_read_sql(sql_file), dialect=dialect, metadata=metadata))
    except SqlToDaxError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    return 0


def _explain_command(sql_file: str, dialect: str, metadata: SemanticModel | None) -> int:
    report = explain(_read_sql(sql_file), dialect=dialect, metadata=metadata)
    payload = {
        "supported": report.supported,
        "dax": report.dax,
        "diagnostic": report.diagnostic.to_dict() if report.diagnostic else None,
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if report.supported else 1


def _read_sql(sql_file: str) -> str:
    if sql_file == "-":
        return sys.stdin.read()
    return Path(sql_file).read_text(encoding="utf-8")
