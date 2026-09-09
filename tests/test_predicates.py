from sql_to_dax import translate


def test_translate_not_equals_predicate() -> None:
    assert translate("SELECT region FROM sales WHERE year != 2026") == (
        "EVALUATE\n"
        "SELECTCOLUMNS(FILTER('sales', 'sales'[year] <> 2026), "
        "\"region\", 'sales'[region])"
    )


def test_translate_comparison_predicate() -> None:
    assert translate("SELECT region FROM sales WHERE revenue >= 100.5") == (
        "EVALUATE\n"
        "SELECTCOLUMNS(FILTER('sales', 'sales'[revenue] >= 100.5), "
        "\"region\", 'sales'[region])"
    )


def test_translate_in_predicate() -> None:
    assert translate("SELECT region FROM sales WHERE region IN ('EMEA', 'APAC')") == (
        "EVALUATE\n"
        "SELECTCOLUMNS(FILTER('sales', 'sales'[region] IN {\"EMEA\", \"APAC\"}), "
        "\"region\", 'sales'[region])"
    )


def test_translate_is_null_predicate() -> None:
    assert translate("SELECT region FROM sales WHERE region IS NULL") == (
        "EVALUATE\n"
        "SELECTCOLUMNS(FILTER('sales', ISBLANK('sales'[region])), "
        "\"region\", 'sales'[region])"
    )


def test_translate_is_not_null_predicate() -> None:
    assert translate("SELECT region FROM sales WHERE region IS NOT NULL") == (
        "EVALUATE\n"
        "SELECTCOLUMNS(FILTER('sales', NOT ISBLANK('sales'[region])), "
        "\"region\", 'sales'[region])"
    )


def test_translate_nested_boolean_predicate() -> None:
    sql = "SELECT region FROM sales WHERE year = 2026 AND (region = 'EMEA' OR region = 'APAC')"

    assert translate(sql) == (
        "EVALUATE\n"
        "SELECTCOLUMNS(FILTER('sales', "
        "('sales'[year] = 2026 AND ('sales'[region] = \"EMEA\" OR "
        "'sales'[region] = \"APAC\"))), "
        "\"region\", 'sales'[region])"
    )
