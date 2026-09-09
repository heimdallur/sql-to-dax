import tomllib
from pathlib import Path

import pytest

from sql_to_dax import translate
from sql_to_dax.errors import UnsupportedSqlError


def _load_cases(path: str) -> list[dict[str, str]]:
    data = tomllib.loads(Path(path).read_text(encoding="utf-8"))
    return list(data["case"])


@pytest.mark.parametrize("case", _load_cases("tests/fixtures/supported.toml"))
def test_supported_golden_queries(case: dict[str, str]) -> None:
    assert translate(case["sql"]) == case["dax"]


@pytest.mark.parametrize("case", _load_cases("tests/fixtures/unsupported.toml"))
def test_unsupported_golden_queries(case: dict[str, str]) -> None:
    with pytest.raises(UnsupportedSqlError) as exc:
        translate(case["sql"])
    assert exc.value.code == case["code"]
