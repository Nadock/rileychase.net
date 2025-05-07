import asyncio
import pathlib

import aiofile
import bs4
import markdown
import yaml

from weaving import emoji, errors, models, pymdx_class_tags


async def read_markdown(path: pathlib.Path) -> tuple[str, models.PageFrontmatter]:
    """
    Read file at path and extract markdown content and any YAML frontmatter separately.

    This does not parse the markdown content in any way, but does parse the YAML
    frontmatter into `types.PageFrontmatter` using `yaml.safe_load`.
    """
    async with aiofile.async_open(path, "r") as f:
        lines = [line async for line in f if isinstance(line, str)]

    # Detect end of frontmatter — idx points to frontmatter end delimiter line
    idx = 0
    if len(lines) > 2 and lines[0] == "---\n":  # noqa: PLR2004
        while idx < len(lines):
            idx += 1
            if idx + 1 < len(lines) and lines[idx] in ["---\n", "...\n"]:
                idx += 1
                break

    raw_fm = yaml.safe_load("".join(lines[1 : idx - 1])) if idx > 0 else {}

    if diff := set(raw_fm).difference(set(models.PageFrontmatter.model_fields)):
        raise errors.WeavingError(f"Page frontmatter field not supported: {diff}")

    fm = models.PageFrontmatter.model_validate(raw_fm)

    return "".join(lines[idx:]), fm


async def render(page: str) -> str:
    """Render markdown content to HTML."""
    md = markdown.Markdown(
        output_format="html",
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
    return await asyncio.to_thread(md.convert, page)


async def preview(page: str) -> str | None:
    """Return a preview of the page by extracting the first paragraph of text."""

    def _bs4_find_p(html: str):  # noqa: ANN202
        return bs4.BeautifulSoup(html, features="html.parser").find("p")

    first_p = await asyncio.to_thread(_bs4_find_p, await render(page))
    return first_p.get_text() if first_p else None
