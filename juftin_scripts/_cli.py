"""
Juftin CLI
"""

import logging
from dataclasses import dataclass
from typing import Optional

import click
from rich import traceback

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


@click.group()
@click.version_option(version=__version__, prog_name=__application__)
@debug_option
@click.pass_context
def cli(ctx: click.core.Context, debug: bool) -> None:
    """
    Juftin's CLI 🚀
    """
    ctx.obj = JuftinContext(debug=debug)
    traceback.install(show_locals=debug)
    logging.basicConfig(
        level=logging.DEBUG if debug is True else logging.INFO,
        format="%(asctime)s [%(levelname)8s]: %(message)s",
    )


@cli.command(name="browse")
@click.argument("path", default=None, required=False, type=click.Path(exists=True))
@click.pass_obj
def browse(context: JuftinContext, path: Optional[str]) -> None:
    """
    Start the TUI File Browser
    """
    config = TextualAppContext(file_path=path, debug=context.debug)
    app = CodeBrowser(config_object=config)
    app.run()


cli.add_command(rotate)

if __name__ == "__main__":
    cli()
