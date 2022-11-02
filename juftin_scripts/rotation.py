#!/usr/bin/env python3

"""
AWS Profile Rotation Script
"""

import configparser
import pathlib
from copy import deepcopy
from typing import Any, Dict, List, Tuple

import rich_click as click
from rich import print, traceback
from rich.console import Console

console = Console()
traceback.install()
aws_dir = pathlib.Path.home().joinpath(".aws").resolve()
config_file = aws_dir.joinpath("config")


def get_parser() -> configparser.ConfigParser:
    """
    Get the parser object
    """
    config_parser = configparser.ConfigParser()
    with config_file.open(mode="r") as config:
        config_parser.read_file(config)
    return config_parser


def get_profiles(parser: configparser.ConfigParser) -> Tuple[List[str], Dict[str, Any]]:
    """
    Get a List of Formatted Profile Names
    """
    config_mapping = {
        section: dict(parser.items(section=section)) for section in parser.sections()
    }
    profile_names_cleaned = [
        section_name.replace("profile ", "")
        for section_name in config_mapping.keys()
        if section_name != "profile default"
    ]
    return profile_names_cleaned, config_mapping


def get_config_section(
    parser: configparser.ConfigParser, profile: str
) -> Tuple[str, Dict[str, str]]:
    """
    Retrieve a desired section from the config

    Parameters
    ----------
    parser: configparser.ConfigParser
    profile: str

    Returns
    -------
    Tuple[str, Dict[str, str]]
    """
    profile_names_cleaned, config_mapping = get_profiles(parser=parser)
    profile_name = f"profile {profile}"
    if profile is None:
        console.print(
            "No profile selected. Available Profiles include: ", style="bold red"
        )
        console.print("\n".join(profile_names_cleaned), style="bold blue")
        exit(1)
    if profile_name == "profile default":
        console.print(
            "Default Profile Rotation Isn't Supported. Available Profiles include:",
            style="bold red",
        )
        console.print("\n".join(profile_names_cleaned), style="bold blue")
        exit(1)
    elif profile_name not in config_mapping:
        console.print(
            f"That profile doesn't exist in the {config_file} file. "
            "Available Profiles include:",
            style="bold red",
        )
        console.print("\n".join(profile_names_cleaned), style="bold blue")
        exit(1)
    return profile_name, config_mapping[profile_name]


def set_parser_section(
    parser: configparser.ConfigParser, options: Dict[str, str]
) -> configparser.ConfigParser:
    """
    Set Values on the parser object

    Parameters
    ----------
    parser: configparser.ConfigParser
    options: Dict[str, str]

    Returns
    -------
    configparser.ConfigParser
    """
    new_parser = deepcopy(parser)
    default_profile_name = "profile default"
    if default_profile_name not in new_parser.sections():
        new_parser.add_section(section=default_profile_name)
    for key, value in options.items():
        new_parser.set(section="profile default", option=key, value=value)
    return new_parser


def write_parser_to_file(parser: configparser.ConfigParser) -> pathlib.Path:
    """
    Write the contents of a ConfigParser to the AWS File

    Parameters
    ----------
    parser: configparser.ConfigParser

    Returns
    -------
    pathlib.Path
    """
    with config_file.open(mode="w") as config:
        parser.write(config)
    return config_file


@click.command("rotate")
@click.argument("profile", required=False)
@click.option(
    "-l",
    "--list",
    "list_profiles",
    is_flag=True,
    default=False,
    help="List Available Profiles",
)
def rotate(profile: str, list_profiles: bool) -> None:
    """
    Rotate a listed AWS Profile to your default profile

    This command line utility overwrites your `default` AWS Profile
    locally and replaces it with another profile.
    """
    parser = get_parser()
    if list_profiles is True or profile is None:
        if profile is None and list_profiles is False:
            console.print(
                "Pass a profile name to rotate AWS profiles. Profiles include:",
                style="bold cyan",
            )
        profile_names, _ = get_profiles(parser=parser)
        for profile_name in profile_names:
            console.print(profile_name, style="bold blue")
        exit(0)
    print(
        f"[bold yellow]Rotating to Profile:[/bold yellow] [italic purple]{profile}[/italic purple]"
    )
    _, options = get_config_section(parser=parser, profile=profile)
    parser = set_parser_section(parser=parser, options=options)
    write_parser_to_file(parser=parser)
    print(
        f"[bold blue]Rotation Complete:[/bold blue] [italic green]{profile}[/italic green]"
    )


if __name__ == "__main__":
    rotate()
