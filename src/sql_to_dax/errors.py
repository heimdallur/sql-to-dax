from __future__ import annotations

from sql_to_dax.diagnostics import Diagnostic


class SqlToDaxError(Exception):
    """Base package exception."""


class UnsupportedSqlError(SqlToDaxError):
    """Raised when SQL syntax or semantics are outside the supported subset."""

    def __init__(self, diagnostic: Diagnostic | str, message: str | None = None) -> None:
        if isinstance(diagnostic, Diagnostic):
            self.diagnostic = diagnostic
        elif message is not None:
            self.diagnostic = Diagnostic(code=diagnostic, message=message)
        else:
            raise TypeError("message is required when diagnostic is a code string")
        self.code = self.diagnostic.code
        self.message = self.diagnostic.message
        super().__init__(f"{self.code}: {self.message}")
