"""Translate a documented subset of Databricks SparkSQL into DAX."""

from sql_to_dax.api import translate
from sql_to_dax.errors import SqlToDaxError, UnsupportedSqlError

__all__ = ["SqlToDaxError", "UnsupportedSqlError", "__version__", "translate"]

__version__ = "0.1.0"
