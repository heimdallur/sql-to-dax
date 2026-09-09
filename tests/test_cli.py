import json
import sys
from pathlib import Path

from sql_to_dax.cli import main


def test_cli_translates_stdin(monkeypatch, capsys) -> None:
    monkeypatch.setattr(sys, "stdin", _TextInput("SELECT region FROM sales"))

    exit_code = main(["-"])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "SELECTCOLUMNS('sales'" in captured.out


def test_cli_translates_file(tmp_path: Path, capsys) -> None:
    query = tmp_path / "query.sql"
    query.write_text("SELECT region FROM sales", encoding="utf-8")

    exit_code = main([str(query)])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "SELECTCOLUMNS('sales'" in captured.out


def test_cli_explain_reports_supported_sql(monkeypatch, capsys) -> None:
    monkeypatch.setattr(sys, "stdin", _TextInput("SELECT region FROM sales"))

    exit_code = main(["explain", "-"])

    payload = json.loads(capsys.readouterr().out)
    assert exit_code == 0
    assert payload["supported"] is True
    assert payload["dax"].startswith("EVALUATE")


def test_cli_explain_reports_unsupported_sql(monkeypatch, capsys) -> None:
    monkeypatch.setattr(sys, "stdin", _TextInput("SELECT * FROM a JOIN b ON a.id = b.id"))

    exit_code = main(["explain", "-"])

    payload = json.loads(capsys.readouterr().out)
    assert exit_code == 1
    assert payload["supported"] is False
    assert payload["diagnostic"]["code"] == "unsupported.join"


def test_cli_reports_unsupported_sql(monkeypatch, capsys) -> None:
    monkeypatch.setattr(sys, "stdin", _TextInput("SELECT * FROM a JOIN b ON a.id = b.id"))

    exit_code = main(["-"])

    captured = capsys.readouterr()
    assert exit_code == 2
    assert "unsupported.join" in captured.err


class _TextInput:
    def __init__(self, value: str) -> None:
        self.value = value

    def read(self) -> str:
        return self.value
