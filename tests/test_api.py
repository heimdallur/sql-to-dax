import pytest

from sql_to_dax import translate
from sql_to_dax.errors import UnsupportedSqlError


def test_translate_projection() -> None:
    assert translate("SELECT region FROM sales") == (
        "EVALUATE\nSELECTCOLUMNS('sales', \"region\", 'sales'[region])"
    )


def test_translate_filtered_grouped_sum_limit() -> None:
    sql = """
    SELECT region, SUM(revenue) AS total_revenue
    FROM sales
    WHERE year = 2026
    GROUP BY region
    ORDER BY total_revenue DESC
    LIMIT 10
    """
    dax = translate(sql)
    assert dax == (
        "EVALUATE\n"
        "TOPN(10, SUMMARIZECOLUMNS('sales'[region], "
        "FILTER('sales', 'sales'[year] = 2026), "
        "\"total_revenue\", SUM('sales'[revenue])), [total_revenue], DESC)"
    )


def test_translate_uses_metadata_mapping() -> None:
    dax = translate(
        "SELECT region FROM sales",
        metadata={"tables": {"sales": {"name": "Sales", "columns": {"region": "Region"}}}},
    )
    assert dax == "EVALUATE\nSELECTCOLUMNS('Sales', \"Region\", 'Sales'[Region])"


def test_unsupported_join_fails_with_code() -> None:
    with pytest.raises(UnsupportedSqlError) as exc:
        translate("SELECT * FROM a JOIN b ON a.id = b.id")
    assert exc.value.code == "unsupported.join"
