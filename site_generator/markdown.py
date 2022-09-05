import os
import pathlib
from typing import AsyncIterator, Tuple

import yaml
from pymdownx import emoji  # type: ignore

import markdown
from site_generator import config, template


async def markdown_pipeline(
    cfg: config.SiteGeneratorConfig, page: pathlib.Path
) -> pathlib.Path:
    """Process a markdown page into an HTML page."""
    content, frontmatter = await load_markdown(page)

    template_name = frontmatter.get("template", cfg.default_template)

    output_path = frontmatter.get("path")
    if not output_path:
        base = page.parent.relative_to(cfg.pages)
        name = page.parts[-1].replace(".md", ".html")
        output_path = base / name
    output_path = (cfg.output / output_path).absolute()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    html = await template.render_template(
        cfg.templates,
        template_name,
        content=content,
        meta=frontmatter,
    )

    output_path.write_text(html)

    return output_path


async def find_markdown(path: pathlib.Path) -> AsyncIterator[pathlib.Path]:
    """
    Find any files Markdown files under a root `path`.

    Current implementation just checks for file names that end in `.md`.
    """
    for dirpath, _, filenames in os.walk(path):
        for filename in filenames:
            if filename.endswith(".md"):
                yield pathlib.Path(dirpath) / filename


async def load_markdown(path: pathlib.Path) -> Tuple[str, dict]:
    """
    Read file at path and extract markdown content and any YAML frontmatter separately.

    This does not parse the markdown content in any way, but does parse the YAML
    frontmatter into a `dict` using `yaml.safe_load`.
    """
    with path.open("r", encoding="utf-8") as file:
        lines = file.readlines()

    if len(lines) < 2:
        # Cannot have frontmatter with less than 2 lines
        return "".join(lines), {}

    # Detect end of frontmatter — idx points to frontmatter end delimiter line
    idx = 0
    if lines[0] == "---\n":
        while idx < len(lines):
            idx += 1
            if idx + 1 < len(lines) and lines[idx] in ["---\n", "...\n"]:
                idx += 1
                break

    content = "".join(lines[idx:])
    frontmatter = yaml.safe_load("".join(lines[1 : idx - 1]))

    return content, frontmatter


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
