from __future__ import annotations


class SqlToDaxError(Exception):
    """Base package exception."""


class UnsupportedSqlError(SqlToDaxError):
    """Raised when SQL syntax or semantics are outside the supported subset."""

    def __init__(self, code: str, message: str) -> None:
        self.code = code
        self.message = message
        super().__init__(f"{code}: {message}")
