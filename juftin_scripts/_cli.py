"""
Juftin CLI
"""

import logging
import sys
from dataclasses import dataclass
from typing import Optional

import rich_click as click
import click as original_click
from rich import traceback
from rich.logging import RichHandler

from juftin_scripts import __application__, __version__
from juftin_scripts._base import TextualAppContext
from juftin_scripts.code_browser import CodeBrowser
from juftin_scripts.rotation import rotate

logger = logging.getLogger(__name__)
traceback.install(show_locals=True)


@dataclass
class JuftinContext:
    """
    Context Object to Pass Around CLI
    """

    debug: bool


debug_option = click.option(
    "--debug/--no-debug", default=False, help="Enable extra debugging output"
)


@click.group(name="juftin")
@click.version_option(version=__version__, prog_name=__application__)
@debug_option
@click.pass_context
def cli(ctx: click.core.Context, debug: bool) -> None:
    """
    Juftin's CLI 🚀

    This Command Line utility has a few tools for developer productivity
    and entertainment.

    Among its useful commands include `browse` for a GUI file browser and
    `rotate` - a tool for altering AWS profiles.
    """
    ctx.obj = JuftinContext(debug=debug)
    traceback.install(show_locals=debug, suppress=[original_click])
    logging.basicConfig(
        level="NOTSET",
        datefmt="[%Y-%m-%d %H:%M:%S]",
        format="%(message)s",
        handlers=[
            RichHandler(
                level=logging.DEBUG if debug is True else logging.INFO,
                omit_repeated_times=False,
                show_path=False,
            )
        ],
    )
    logger.debug("juftin Version: %s", __version__)
    logger.debug("Python Version: %s", sys.version.split(" ")[0])
    logger.debug("Platform: %s", sys.platform)


@cli.command(name="browse")
@click.argument("path", default=None, required=False, type=click.Path(exists=True))
@click.pass_obj
def browse(context: JuftinContext, path: Optional[str]) -> None:
    """
    Start the TUI File Browser

    This utility displays a TUI (textual user interface) application. The application
    allows you to visually browse through a repository and display the contents of its
    files
    """
    config = TextualAppContext(file_path=path, debug=context.debug)
    app = CodeBrowser(config_object=config)
    app.run()


cli.add_command(rotate)

if __name__ == "__main__":
    cli()
