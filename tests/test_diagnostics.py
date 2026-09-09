import pytest

from sql_to_dax import explain, translate
from sql_to_dax.diagnostics import Diagnostic, TranslationReport
from sql_to_dax.errors import UnsupportedSqlError


def test_diagnostic_has_stable_public_shape() -> None:
    diagnostic = Diagnostic(
        code="unsupported.join",
        message="JOIN is not supported yet",
        hint="Model relationships are required before joins can be translated safely.",
        docs_url="https://github.com/heimdallur/sql-to-dax/blob/main/docs/support-matrix.md#join",
    )

    assert diagnostic.to_dict() == {
        "code": "unsupported.join",
        "message": "JOIN is not supported yet",
        "hint": "Model relationships are required before joins can be translated safely.",
        "docs_url": "https://github.com/heimdallur/sql-to-dax/blob/main/docs/support-matrix.md#join",
    }


def test_unsupported_sql_error_exposes_diagnostic() -> None:
    diagnostic = Diagnostic(code="unsupported.cte", message="CTEs are not supported yet")
    error = UnsupportedSqlError(diagnostic)

    assert error.code == "unsupported.cte"
    assert error.diagnostic == diagnostic
    assert str(error) == "unsupported.cte: CTEs are not supported yet"


def test_explain_returns_report_for_supported_sql() -> None:
    report = explain("SELECT region FROM sales")

    assert isinstance(report, TranslationReport)
    assert report.supported is True
    assert report.dax == "EVALUATE\nSELECTCOLUMNS('sales', \"region\", 'sales'[region])"
    assert report.diagnostic is None


def test_explain_returns_diagnostic_for_unsupported_sql() -> None:
    report = explain("SELECT * FROM a JOIN b ON a.id = b.id")

    assert report.supported is False
    assert report.dax is None
    assert report.diagnostic is not None
    assert report.diagnostic.code == "unsupported.join"


def test_translate_still_raises_for_unsupported_sql() -> None:
    with pytest.raises(UnsupportedSqlError):
        translate("WITH x AS (SELECT region FROM sales) SELECT region FROM x")
