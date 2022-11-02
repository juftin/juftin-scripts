"""
Juftin CLI
"""

import logging
import sys
from typing import List

import click as original_click
import rich_click as click
from click.core import Context
from rich import traceback
from rich.logging import RichHandler

from juftin_scripts import __application__, __version__
from juftin_scripts._base import JuftinClickContext
from juftin_scripts.code_browser import browse
from juftin_scripts.rotation import rotate

logger = logging.getLogger(__name__)

debug_option = click.option(
    "--debug/--no-debug", default=False, help="Enable extra debugging output"
)


@click.group(name="juftin")
@click.version_option(version=__version__, prog_name=__application__)
@debug_option
@click.pass_context
def cli(ctx: Context, debug: bool) -> None:
    """
    Juftin's CLI 🚀

    This Command Line utility has a few tools for developer productivity
    and entertainment.

    Among its useful commands include `browse` for a GUI file browser and
    `rotate` - a tool for altering AWS profiles.
    """
    ctx.obj = JuftinClickContext(debug=debug)
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


# noinspection PyTypeChecker
commands: List[click.Command] = [rotate, browse]

for cli_command in commands:
    cli.add_command(cli_command)

if __name__ == "__main__":
    cli()
