# juftin-scripts

Helpful Python scripts by [@juftin](https://github.com/juftin)

## Installation

Using [pipx](https://pypa.github.io/pipx/)

```shell
pipx install juftin-scripts
```

Using pip

```shell
pip install juftin-scripts
```

## CLI Reference

::: mkdocs-click
    :module: juftin_scripts.__main__
    :command: cli

## browse

If you'd like to use the `browse` CLI to view parquet files,
install it with the `parquet` extra:

```shell
pipx install "juftin-scripts[parquet]"
```

If you'd like to use the `browse` CLI to view files on remote
filesystems like AWS S3 or Google Cloud Storage, install it with the
`fsspec` extra.

```shell
pipx install "juftin-scripts[fsspec]"
```

To install all extras, use the `all` extra:

```shell
pipx install "juftin-scripts[all]"
```

___________
___________

<br/>

<p align="center"><a href="https://github.com/juftin"><img src="https://raw.githubusercontent.com/juftin/juftin/main/static/juftin.png" width="120" height="120" alt="logo"></p>
