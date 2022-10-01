import datetime
import os
import pathlib
from typing import Any, AsyncIterator, Tuple

import markdown
import yaml

from site_generator import blog, config, emoji, errors, frontmatter, logging, template

LOGGER = logging.getLogger()


async def markdown_pipeline(
    cfg: config.SiteGeneratorConfig, path: pathlib.Path
) -> pathlib.Path:
    """Process a markdown page into an HTML page."""
    try:
        content, fm = await load_markdown(path)
        fm.config = cfg
    except Exception as ex:
        raise errors.PipelineError(
            f"Unable to read markdown file {cfg.format_relative_path(path)}: {ex}"
        ) from ex

    render_kwargs = {
        "content": await render(content),
        "props": fm.get_props(),
        "meta": fm.get_meta(),
        "info": get_template_info(cfg),
    }

    if fm.type == "blog_index":
        render_kwargs["blog"] = await blog.blog_index_render_info(cfg, path)

    try:
        html = await template.render_template(
            templates=cfg.templates, name=fm.get_template_name(), **render_kwargs
        )
    except Exception as ex:
        raise errors.PipelineError(
            f"Rendering HTML for {cfg.format_relative_path(path)} failed: {ex}"
        ) from ex

    output = fm.get_output_path()
    output.parent.mkdir(parents=True, exist_ok=True)
    try:
        output.write_text(html)
    except Exception as ex:
        raise errors.PipelineError(
            f"Failed to write output file {cfg.format_relative_path(output)}: {ex}"
        ) from ex

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


async def load_markdown(path: pathlib.Path) -> Tuple[str, frontmatter.PageFrontmatter]:
    """
    Read file at path and extract markdown content and any YAML frontmatter separately.

    This does not parse the markdown content in any way, but does parse the YAML
    frontmatter into a `dict` using `yaml.safe_load`.
    """
    with path.open("r", encoding="utf-8") as file:
        lines = file.readlines()

    # Detect end of frontmatter — idx points to frontmatter end delimiter line
    idx = 0
    if len(lines) > 2 and lines[0] == "---\n":
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


def get_template_info(cfg: config.SiteGeneratorConfig) -> dict[str, Any]:
    """
    Populate and return a `dict` of general purpose information about an individual
    template render.
    """
    info: dict[str, Any] = {
        "rendered_at": datetime.datetime.now().astimezone(),
        "ref": None,
    }

    git_head = cfg.base / ".git" / "HEAD"
    try:
        ref = git_head.read_text("utf-8").strip().replace("ref: ", "")
        info["ref"] = (cfg.base / ".git" / ref).read_text("utf-8").strip()
    except Exception as ex:  # pylint: disable=broad-except
        LOGGER.warning(f"Unable to read git ref: {ex}")

    return info
