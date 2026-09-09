from sql_to_dax import translate


def test_golden_queries() -> None:
    cases = {
        "SELECT region FROM sales": (
            "EVALUATE\nSELECTCOLUMNS('sales', \"region\", 'sales'[region])"
        ),
        "SELECT region FROM sales WHERE year = 2026": (
            "EVALUATE\n"
            "SELECTCOLUMNS(FILTER('sales', 'sales'[year] = 2026), "
            "\"region\", 'sales'[region])"
        ),
        "SELECT region, COUNT(*) AS rows FROM sales GROUP BY region": (
            "EVALUATE\nSUMMARIZECOLUMNS('sales'[region], "
            "\"rows\", COUNTROWS('sales'))"
        ),
    }
    for sql, dax in cases.items():
        assert translate(sql) == dax
