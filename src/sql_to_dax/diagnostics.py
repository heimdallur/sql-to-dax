from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Diagnostic:
    """Structured translation diagnostic for unsupported or unsafe SQL."""

    code: str
    message: str
    hint: str | None = None
    docs_url: str | None = None

    def to_dict(self) -> dict[str, str | None]:
        return {
            "code": self.code,
            "message": self.message,
            "hint": self.hint,
            "docs_url": self.docs_url,
        }


@dataclass(frozen=True)
class TranslationReport:
    """Non-throwing explanation result for a translation attempt."""

    supported: bool
    dax: str | None = None
    diagnostic: Diagnostic | None = None
