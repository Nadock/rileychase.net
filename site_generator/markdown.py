from __future__ import annotations

import datetime
import os
import pathlib
from typing import TYPE_CHECKING, Any

import markdown
import yaml

from site_generator import (
    blog,
    config,
    emoji,
    errors,
    frontmatter,
    logging,
    pymdx_class_tags,
    template,
)

if TYPE_CHECKING:
    from collections.abc import AsyncIterator

LOGGER = logging.getLogger()


async def markdown_pipeline(
    cfg: config.SiteGeneratorConfig, path: pathlib.Path
) -> pathlib.Path | None:
    """Process a markdown page into an HTML page."""
    try:
        return await _markdown_pipeline(cfg, path)
    except Exception as ex:
        raise errors.PipelineError(
            f"Render pipeline failure for {cfg.format_relative_path(path)}: {ex}"
        ) from ex


async def _markdown_pipeline(
    cfg: config.SiteGeneratorConfig, path: pathlib.Path
) -> pathlib.Path | None:
    content, fm = await load_markdown(cfg, path)
    if fm.type == "debug" and not cfg.debug_pages:
        LOGGER.debug(f"Skipping debug markdown page: {path}")
        return None

    render_kwargs: dict[str, Any] = {
        "content": await render(content),
        "props": fm.get_props(),
        "meta": fm.get_meta(),
        "info": get_template_info(cfg, path),
    }

    if fm.type == "blog_index":
        return await blog.blog_index_pipeline(cfg, path, fm, render_kwargs)

    html = await template.render_template(
        templates=cfg.templates,
        name=fm.get_template_name(),
        **render_kwargs,
    )

    output = fm.get_output_path()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(html)

    LOGGER.debug(
        f"Markdown pipeline converted {cfg.format_relative_path(path)} "
        f"to {cfg.format_relative_path(output)}"
    )
    return output


async def find_markdown(path: pathlib.Path) -> AsyncIterator[pathlib.Path]:
    """
    Find any files Markdown files under a root `path`.

    Current implementation just checks for file names that end in `.md`.
    """
    for dirpath, _, filenames in os.walk(path):
        for filename in filenames:
            if filename.endswith(".md"):
                yield pathlib.Path(dirpath) / filename


async def load_markdown(
    cfg: config.SiteGeneratorConfig, path: pathlib.Path
) -> tuple[str, frontmatter.PageFrontmatter]:
    """
    Read file at path and extract markdown content and any YAML frontmatter separately.

    This does not parse the markdown content in any way, but does parse the YAML
    frontmatter into `frontmatter.PageFrontmatter` using `yaml.safe_load`.
    """
    with path.open("r", encoding="utf-8") as file:
        lines = file.readlines()

    # Detect end of frontmatter — idx points to frontmatter end delimiter line
    idx = 0
    if len(lines) > 2 and lines[0] == "---\n":  # noqa: PLR2004
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
    fm.config = cfg

    return content, fm


async def render(content: str | None) -> str:
    """Render Markdown content to HTML."""
    if not content:
        return ""

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
            pymdx_class_tags.ClassTags(),
        ],
        output_format="html",
        extension_configs={
            "pymdownx.emoji": {
                "emoji_index": emoji.to_markdown_db,
                "emoji_generator": emoji.to_unicode_emoji,
            },
            "pymdownx.tasklist": {
                "custom_checkbox": True,
            },
        },
    )
    return md.convert(content)


def get_template_info(
    cfg: config.SiteGeneratorConfig, path: pathlib.Path
) -> dict[str, str | datetime.datetime]:
    """
    Populate and return a `dict` of general purpose information about an individual
    template render.
    """
    info: dict[str, str | datetime.datetime] = {}

    # Output render timestamp
    info["rendered_at"] = datetime.datetime.now(datetime.UTC)

    # Source file last modified time
    try:
        info["modified_at"] = datetime.datetime.fromtimestamp(
            path.stat().st_mtime, datetime.UTC
        )
    except OSError as ex:
        LOGGER.warning(f"Unable to read file modified time: {ex}")

    # Current git SHA
    git_head = cfg.base / ".git" / "HEAD"
    try:
        ref = git_head.read_text("utf-8").strip().replace("ref: ", "")
        info["ref"] = (cfg.base / ".git" / ref).read_text("utf-8").strip()
    except Exception as ex:
        LOGGER.warning(f"Unable to read git ref: {ex}")

    return info
