"""
Code browser example.

Run with:
    python code_browser.py PATH
"""

import pathlib
from os import getenv
from typing import Any, Iterable, List, Optional, Union

import pandas as pd
import rich_click as click
from art import text2art
from rich import traceback
from rich.markdown import Markdown
from rich.syntax import Syntax
from rich.table import Table
from rich.traceback import Traceback
from textual.containers import Container, Vertical
from textual.reactive import var
from textual.widget import Widget
from textual.widgets import DirectoryTree, Footer, Header, Static

from juftin_scripts._base import JuftinClickContext, JuftinTextualApp, TextualAppContext

favorite_themes: List[str] = [
    "monokai",
    "material",
    "dracula",
    "solarized-light",
    "one-dark",
    "solarized-dark",
    "emacs",
    "vim",
    "github-dark",
    "native",
    "paraiso-dark",
]

rich_default_theme = getenv("RICH_THEME", False)
if rich_default_theme in favorite_themes:
    assert isinstance(rich_default_theme, str)
    favorite_themes.remove(rich_default_theme)
if rich_default_theme is not False:
    assert isinstance(rich_default_theme, str)
    favorite_themes.insert(0, rich_default_theme)


class CodeBrowser(JuftinTextualApp):
    """
    Textual code browser app.
    """

    CSS_PATH = "code_browser.css"
    BINDINGS = [
        ("f", "toggle_files", "Toggle Files"),
        ("q", "quit", "Quit"),
        ("t", "theme", "Toggle Rich Theme"),
    ]

    show_tree = var(True)
    theme_index = var(0)
    rich_themes = favorite_themes
    selected_file_path: Union[pathlib.Path, None, var[None]] = var(None)
    force_show_tree = var(False)

    traceback.install(show_locals=True)

    def watch_show_tree(self, show_tree: bool) -> None:
        """
        Called when show_tree is modified.
        """
        self.set_class(show_tree, "-show-tree")

    def compose(self) -> Iterable[Widget]:  # noqa
        """
        Compose our UI.
        """
        assert isinstance(self.config_object, TextualAppContext)
        file_path = self.config_object.path
        if file_path.is_file():
            self.selected_file_path = file_path
            file_path = file_path.parent
        elif file_path.is_dir() and file_path.joinpath("README.md").exists():
            self.selected_file_path = file_path.joinpath("README.md")
            self.force_show_tree = True
        self.header = Header()
        yield self.header
        self.directory_tree = Vertical(DirectoryTree(str(file_path)), id="tree-view")
        self.code_view = Vertical(Static(id="code", expand=True), id="code-view")
        self.container = Container(self.directory_tree, self.code_view)
        yield self.container
        self.footer = Footer()
        yield self.footer

    def render_document(self, document: pathlib.Path) -> Union[Syntax, Markdown, Table]:
        """
        Render a Code Doc Given Its Extension

        Parameters
        ----------
        document: pathlib.Path
            File Path to Render

        Returns
        -------
        Union[Syntax, Markdown, Table]
        """
        if document.suffix == ".md":
            return Markdown(
                document.read_text(encoding="utf-8"),
                code_theme=self.rich_themes[self.theme_index],
                hyperlinks=True,
            )
        elif document.suffix == ".csv":
            df = pd.read_csv(document, nrows=500)
            return self.df_to_table(pandas_dataframe=df, rich_table=Table())
        elif document.suffix == ".parquet":
            df = pd.read_parquet(document)[:500]
            return self.df_to_table(pandas_dataframe=df, rich_table=Table())
        else:
            return Syntax.from_path(
                str(document),
                line_numbers=True,
                word_wrap=False,
                indent_guides=True,
                theme=self.rich_themes[self.theme_index],
            )

    def render_code_page(
        self,
        file_path: pathlib.Path,
        scroll_home: bool = True,
        content: Optional[Any] = None,
    ) -> None:
        """
        Render the Code Page with Rich Syntax
        """
        code_view = self.query_one("#code", Static)
        font = "univers"
        if content is not None:
            code_view.update(text2art(content, font=font))
            return
        try:
            element = self.render_document(document=file_path)
        except UnicodeError:
            code_view.update(
                text2art("ENCODING", font=font) + "\n\n" + text2art("ERROR", font=font)
            )
            self.sub_title = f"ERROR [{self.rich_themes[self.theme_index]}]"
        except Exception:  # noqa
            code_view.update(
                Traceback(theme=self.rich_themes[self.theme_index], width=None)
            )
            self.sub_title = "ERROR" + f" [{self.rich_themes[self.theme_index]}]"
        else:
            code_view.update(element)
            if scroll_home is True:
                self.query_one("#code-view").scroll_home(animate=False)
            self.sub_title = f"{file_path} [{self.rich_themes[self.theme_index]}]"

    def on_mount(self) -> None:
        """
        On Application Mount - See If a File Should be Displayed
        """
        if self.selected_file_path is not None:
            self.show_tree = self.force_show_tree
            self.render_code_page(file_path=self.selected_file_path)
        else:
            self.show_tree = True
            self.render_code_page(file_path=pathlib.Path.cwd(), content="BROWSE")

    def on_directory_tree_file_click(self, event: DirectoryTree.FileClick) -> None:
        """
        Called when the user click a file in the directory tree.
        """
        self.selected_file_path = pathlib.Path(event.path)
        self.render_code_page(file_path=pathlib.Path(event.path))

    def action_toggle_files(self) -> None:
        """
        Called in response to key binding.
        """
        self.show_tree = not self.show_tree

    def action_theme(self) -> None:
        """
        An action to toggle rich theme.
        """
        if self.selected_file_path is None:
            return
        elif self.theme_index < len(self.rich_themes) - 1:
            self.theme_index += 1
        else:
            self.theme_index = 0
        self.render_code_page(file_path=self.selected_file_path, scroll_home=False)


@click.command(name="browse")
@click.argument("path", default=None, required=False, type=click.Path(exists=True))
@click.pass_obj
def browse(context: JuftinClickContext, path: Optional[str]) -> None:
    """
    Start the TUI File Browser

    This utility displays a TUI (textual user interface) application. The application
    allows you to visually browse through a repository and display the contents of its
    files
    """
    config = TextualAppContext(file_path=path, debug=context.debug)
    app = CodeBrowser(config_object=config)
    app.run()


_config = TextualAppContext(file_path=None)
_app = CodeBrowser(config_object=_config)

if __name__ == "__main__":
    browse()
