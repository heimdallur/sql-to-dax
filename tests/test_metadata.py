from pathlib import Path

from sql_to_dax.metadata import SemanticModel


def test_loads_toml_metadata(tmp_path: Path) -> None:
    model = tmp_path / "model.toml"
    model.write_text('[tables.sales]\nname="Sales"\n[tables.sales.columns]\nregion="Region"\n')
    metadata = SemanticModel.from_toml(model)
    assert metadata.table_name("sales") == "Sales"
    assert metadata.column_name("sales", "region") == "Region"
