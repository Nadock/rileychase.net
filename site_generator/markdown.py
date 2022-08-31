import dataclasses
import os
import pathlib

import yaml

import markdown


def find_markdown(path: pathlib.Path) -> list[pathlib.Path]:
    """
    Find any files Markdown files under a root `path`.

    Current implementation just checks for file names that end in `.md`.
    """
    markdown_paths: list[pathlib.Path] = []

    for dirpath, _, filenames in os.walk(path):
        for filename in filenames:
            if filename.endswith(".md"):
                markdown_paths.append(pathlib.Path(dirpath) / filename)

    return markdown_paths


def load_markdown(path: pathlib.Path):
    md = markdown.Markdown(
        extensions=["full_yaml_metadata"],
        extension_configs={
            "full_yaml_metadata": {"yaml_loader": yaml.SafeLoader},
        },
    )

    html = md.convert(path.read_text("utf-8"))
    meta = md.Meta

    print(f"load_markdown({path=}) => {html=}")
    print(f"load_markdown({path=}) => {meta=}")
