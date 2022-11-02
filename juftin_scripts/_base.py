"""
Extension Classes
"""

from __future__ import annotations

import pathlib
from dataclasses import dataclass
from typing import Any, Dict, Optional

from pandas import DataFrame
from rich.table import Table
from textual.app import App


@dataclass
class TextualAppContext:
    """
    App Context Object
    """

    file_path: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    debug: bool = False

    @property
    def path(self) -> pathlib.Path:
        """
        Resolve `file_path` to a pathlib.Path object
        """
        return (
            pathlib.Path(self.file_path).resolve()
            if self.file_path
            else pathlib.Path.cwd().resolve()
        )


class JuftinTextualApp(App[str]):
    """
    textual.app.App Extension
    """

    def __init__(
        self,
        config_object: Optional[TextualAppContext] = None,
    ):
        """
        Like the textual.app.App class, but with an extra config_object property

        Parameters
        ----------
        config_object: Optional[TextualAppContext]
            A configuration object. This is an optional python object,
            like a dictionary to pass into an application
        """
        super().__init__()
        self.config_object = config_object

    @staticmethod
    def df_to_table(
        pandas_dataframe: DataFrame,
        rich_table: Table,
        show_index: bool = True,
        index_name: Optional[str] = None,
    ) -> Table:
        """
        Convert a pandas.DataFrame obj into a rich.Table obj.

        Parameters
        ----------
        pandas_dataframe: DataFrame
            A Pandas DataFrame to be converted to a rich Table.
        rich_table: Table
            A rich Table that should be populated by the DataFrame values.
        show_index: bool
            Add a column with a row count to the table. Defaults to True.
        index_name: Optional[str]
            The column name to give to the index column. Defaults to None, showing no value.

        Returns
        -------
        Table
            The rich Table instance passed, populated with the DataFrame values.
        """
        if show_index:
            index_name = str(index_name) if index_name else ""
            rich_table.add_column(index_name)

        for column in pandas_dataframe.columns:
            rich_table.add_column(str(column))

        for index, value_list in enumerate(pandas_dataframe.values.tolist()):
            row = [str(index)] if show_index else []
            row += [str(x) for x in value_list]
            rich_table.add_row(*row)

        return rich_table


@dataclass
class JuftinClickContext:
    """
    Context Object to Pass Around CLI
    """

    debug: bool
