import subprocess
import sys


def test_cli_translates_stdin() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "sql_to_dax", "-"],
        input="SELECT region FROM sales",
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0
    assert "SELECTCOLUMNS('sales'" in result.stdout


def test_cli_reports_unsupported_sql() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "sql_to_dax", "-"],
        input="SELECT * FROM a JOIN b ON a.id = b.id",
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 2
    assert "unsupported.join" in result.stderr
