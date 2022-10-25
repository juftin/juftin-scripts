"""
Code browser example.

Run with:
    python code_browser.py PATH
"""

import pathlib
import sys
from typing import Iterable, List, Optional

from rich.syntax import Syntax
from rich.traceback import Traceback
from textual import log
from textual.app import App
from textual.containers import Container, Vertical
from textual.reactive import var
from textual.widget import Widget
from textual.widgets import DirectoryTree, Footer, Header, Static

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


class CodeBrowser(App):  # type: ignore
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

    def watch_show_tree(self, show_tree: bool) -> None:
        """
        Called when show_tree is modified.
        """
        self.set_class(show_tree, "-show-tree")

    def compose(self) -> Iterable[Widget]:
        """
        Compose our UI.
        """
        _file_path = pathlib.Path("./" if len(sys.argv) < 2 else sys.argv[1]).resolve()
        if _file_path.is_file() and _file_path.exists():
            self.selected_file_path = str(_file_path)  # type: ignore
            _file_path = _file_path.parent
        path = str(_file_path)
        yield Header()
        yield Container(
            Vertical(DirectoryTree(path), id="tree-view"),
            Vertical(Static(id="code", expand=True), id="code-view"),
        )
        yield Footer()

    def render_code_page(
        self, file_path: Optional[str], scroll_home: bool = True
    ) -> None:
        """
        Render the Code Page with Rich Syntax
        """
        if file_path is None:
            return
        code_view = self.query_one("#code", Static)
        try:
            syntax = Syntax.from_path(
                file_path,
                line_numbers=True,
                word_wrap=False,
                indent_guides=True,
                theme=self.rich_themes[self.theme_index],
            )
        except Exception:
            code_view.update(
                Traceback(theme=self.rich_themes[self.theme_index], width=None)
            )
            self.sub_title = "ERROR" + f" [{self.rich_themes[self.theme_index]}]"
        else:
            code_view.update(syntax)
            if scroll_home is True:
                self.query_one("#code-view").scroll_home(animate=False)
            self.sub_title = file_path + f" [{self.rich_themes[self.theme_index]}]"

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
        self.selected_file_path = event.path  # type: ignore
        self.render_code_page(file_path=event.path)

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
            log.info(self.theme_index, self.rich_themes[self.theme_index])
        else:
            self.theme_index = 0
        self.render_code_page(file_path=self.selected_file_path, scroll_home=False)


def main() -> None:
    """
    Run the Textual TUI App
    """
    CodeBrowser().run()


if __name__ == "__main__":
    main()
