import os
import pathlib
from typing import AsyncIterator, Tuple

import markdown
import pydantic
import yaml
from pymdownx import emoji  # type: ignore

from site_generator import config, file_util, frontmatter, logging, template

LOGGER = logging.getLogger()


async def markdown_pipeline(
    cfg: config.SiteGeneratorConfig, path: pathlib.Path
) -> pathlib.Path:
    """Process a markdown page into an HTML page."""
    LOGGER.debug(f"Processing markdown file {path=}")

    try:
        content, fm = await load_markdown(path)
    except pydantic.ValidationError as ex:
        LOGGER.error(
            f"Unable to process markdown from {path} due to a frontmatter error: {ex}"
        )
        raise ex

    fm.config = cfg

    template_name = fm.get_template_name()
    output_path = fm.get_output_path()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if not fm.is_outdated() and not cfg.force_rebuild:
        return output_path

    html = await template.render_template(
        templates=cfg.templates,
        name=template_name,
        **{
            "content": await render(content),
            "meta": fm.dict(),
        },
    )

    output_path.write_text(html)
    LOGGER.debug(f"Markdown pipeline output written to {output_path}")
    return output_path


async def find_markdown(path: pathlib.Path) -> AsyncIterator[pathlib.Path]:
    """
    Find any files Markdown files under a root `path`.

    Current implementation just checks for file names that end in `.md`.
    """
    for dirpath, _, filenames in os.walk(path):
        for filename in filenames:
            if filename.endswith(".md"):
                path = pathlib.Path(dirpath) / filename
                LOGGER.debug(f"Found markdown file at {path}")
                yield path


async def load_markdown(path: pathlib.Path) -> Tuple[str, frontmatter.PageFrontmatter]:
    """
    Read file at path and extract markdown content and any YAML frontmatter separately.

    This does not parse the markdown content in any way, but does parse the YAML
    frontmatter into a `dict` using `yaml.safe_load`.
    """
    with path.open("r", encoding="utf-8") as file:
        lines = file.readlines()

    if len(lines) < 2:
        # Cannot have frontmatter with less than 2 lines
        return "".join(lines), frontmatter.PageFrontmatter(file=path)

    # Detect end of frontmatter — idx points to frontmatter end delimiter line
    idx = 0
    if lines[0] == "---\n":
        while idx < len(lines):
            idx += 1
            if idx + 1 < len(lines) and lines[idx] in ["---\n", "...\n"]:
                idx += 1
                break

    content = "".join(lines[idx:])

    page_fm = {}
    if idx > 0:
        page_fm = yaml.safe_load("".join(lines[1 : idx - 1]))
    fm = frontmatter.PageFrontmatter(file=path, **page_fm)

    return content, fm


async def render(content: str) -> str:
    """Render Markdown content to HTML."""
    md = markdown.Markdown(
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
    )
    return md.convert(content)
