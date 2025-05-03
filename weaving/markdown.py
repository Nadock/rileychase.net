import asyncio
import pathlib

import aiofile
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


class MarkdownRender:
    """Render markdown pages."""

    def __init__(self) -> None:
        self.md = markdown.Markdown(
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
        self._lock = asyncio.Lock()

    async def render(self, page: str) -> str:
        """Render a markdown page to HTML."""
        if not page:
            return ""
        async with self._lock:
            return self.md.convert(page)
