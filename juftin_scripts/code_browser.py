"""
Code browser example.

Run with:
    python code_browser.py PATH
"""
import io
import pathlib
from os import getenv
from sys import argv
from typing import Iterable, List, Optional, Union

import cv2
import numpy as np
import pandas as pd
from art import text2art
from rich import traceback
from rich.markdown import Markdown
from rich.syntax import Syntax
from rich.table import Table
from textual.containers import Container, Vertical
from textual.reactive import var
from textual.widget import Widget
from textual.widgets import DirectoryTree, Footer, Header, Static

from juftin_scripts._base import JuftinTextualApp, TextualAppContext

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


def image_to_text(file_path):
    """
    Convert an Image to ASCII Text
    """
    CHAR_LIST = (
        "$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\|()1{}[]?-_+~<>i!lI;:,\"^`'. "
    )
    num_chars = len(CHAR_LIST)
    num_cols = 150
    image = cv2.imread(file_path)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    height, width = image.shape
    cell_width = width / 150
    cell_height = 2 * cell_width
    num_rows = int(height / cell_height)
    if num_cols > width or num_rows > height:
        print("Too many columns or rows. Use default setting")
        cell_width = 6
        cell_height = 12
        num_cols = int(width / cell_width)
        num_rows = int(height / cell_height)

    output_file = io.StringIO()
    for i in range(num_rows):
        for j in range(num_cols):
            output_file.write(
                CHAR_LIST[
                    min(
                        int(
                            np.mean(
                                image[
                                    int(i * cell_height) : min(
                                        int((i + 1) * cell_height), height
                                    ),
                                    int(j * cell_width) : min(
                                        int((j + 1) * cell_width), width
                                    ),
                                ]
                            )
                            * num_chars
                            / 255
                        ),
                        num_chars - 1,
                    )
                ]
            )
        output_file.write("\n")
    output_file.seek(0)
    text = output_file.read()
    return text


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
    selected_file_path = var(None)

    # traceback.install(show_locals=True)

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
        if self.config_object.file_path is None:
            file_path = pathlib.Path.cwd()
        else:
            file_path = self.config_object.path
            if file_path.is_file():
                self.selected_file_path = file_path
                file_path = file_path.parent
        self.header = Header()
        yield self.header
        self.directory_tree = Vertical(DirectoryTree(str(file_path)), id="tree-view")
        self.code_view = Vertical(Static(id="code", expand=True), id="code-view")
        self.container = Container(self.directory_tree, self.code_view)
        yield self.container
        self.footer = Footer()
        yield self.footer

    def render_document(self, document: pathlib.Path) -> Union[Syntax, Markdown]:
        """
        Render a Code Doc Given Its Extension

        Parameters
        ----------
        document: pathlib.Path
            File Path to Render

        Returns
        -------
        Union[Syntax, Markdown]
        """
        if document.suffix == ".md":
            element = Markdown(
                document.read_text(encoding="utf-8"),
                code_theme=self.rich_themes[self.theme_index],
                hyperlinks=True,
            )
        elif document.suffix == ".csv":
            df = pd.read_csv(document, nrows=500)
            element = self.df_to_table(pandas_dataframe=df, rich_table=Table())
        elif document.suffix == ".parquet":
            df = pd.read_parquet(document)[:500]
            element = self.df_to_table(pandas_dataframe=df, rich_table=Table())
        elif document.suffix in [".png", ".jpg", ".jpeg"]:
            element = image_to_text(document)
        else:
            element = Syntax.from_path(
                str(document),
                line_numbers=True,
                word_wrap=False,
                indent_guides=True,
                theme=self.rich_themes[self.theme_index],
            )
        return element

    def render_code_page(
        self, file_path: Optional[pathlib.Path], scroll_home: bool = True
    ) -> None:
        """
        Render the Code Page with Rich Syntax
        """
        if file_path is None:
            return
        code_view = self.query_one("#code", Static)
        try:
            element = self.render_document(document=file_path)
        except Exception:  # noqa
            font = "block"
            code_view.update(
                # traceback.Traceback(theme=self.rich_themes[self.theme_index], width=None, show_locals=True)
                text2art("ENCODING", font=font)
                + "\n\n"
                + text2art("ERROR", font=font)
            )
            self.sub_title = f"ERROR [{self.rich_themes[self.theme_index]}]"
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
            self.show_tree = False
            self.render_code_page(file_path=self.selected_file_path)

    def on_directory_tree_file_click(self, event: DirectoryTree.FileClick) -> None:
        """
        Called when the user click a file in the directory tree.
        """
        self.selected_file_path = pathlib.Path(event.path)  # type: ignore
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


if __name__ == "__main__":
    file_path_arg = None if len(argv) == 1 else argv[1]
    config = TextualAppContext(file_path=file_path_arg)
    app = CodeBrowser(config_object=config)
    app.run()
