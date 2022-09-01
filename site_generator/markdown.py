import dataclasses
import os
import pathlib

import yaml
from pymdownx import emoji  # type: ignore

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


@dataclasses.dataclass
class MarkdownFile:
    """
    A `MarkdownFile` is a collection of the raw Markdown formatted contents of a file
    and any YAML frontmatter that is present.
    """

    content: str
    frontmatter: dict

    def render(self) -> str:
        """Render the content of this `MarkdownFile` as HTML."""
        return markdown.Markdown(
            extensions=[
                "markdown.extensions.tables",
                "markdown.extensions.fenced_code",
                "markdown.extensions.codehilite",
                "pymdownx.betterem",
                "pymdownx.emoji",
                "pymdownx.highlight",
                "pymdownx.magiclink",
                "pymdownx.saneheaders",
                "pymdownx.tasklist",
                "pymdownx.tilde",
                "nl2br",
            ],
            output_format="html",
            extension_configs={
                "pymdownx.emoji": {
                    "emoji_index": emoji.gemoji,
                    "emoji_generator": emoji.to_svg,
                },
                "pymdownx.tasklist": {
                    "custom_checkbox": True,
                },
            },
        ).convert(self.content)


def load_markdown(path: pathlib.Path) -> MarkdownFile:
    """
    Read file at path and extract markdown content and any YAML frontmatter separately.

    This does not parse the markdown content in any way, but does parse the YAML
    frontmatter into a `dict` using `yaml.safe_load`.
    """
    with path.open("r", encoding="utf-8") as file:
        lines = file.readlines()

    if len(lines) < 2:
        # Cannot have frontmatter with less than 2 lines
        return MarkdownFile(content="".join(lines), frontmatter={})

    # Detect end of frontmatter — idx points to frontmatter end delimiter line
    idx = 0
    if lines[0] == "---\n":
        while idx < len(lines):
            idx += 1
            if idx + 1 < len(lines) and lines[idx] in ["---\n", "...\n"]:
                idx += 1
                break

    return MarkdownFile(
        content="".join(lines[idx:]),
        frontmatter=yaml.safe_load("".join(lines[1 : idx - 1])),
    )
