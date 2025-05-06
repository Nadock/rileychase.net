import asyncio
import datetime
import pathlib
from collections.abc import AsyncGenerator
from typing import assert_never

import aiofile

from weaving import errors, log, markdown, models
from weaving import templates as weaving_templates

from .pipeline import Pipeline


class PagePipeline(Pipeline):
    def __init__(
        self, *, root: pathlib.Path, output: pathlib.Path, templates: pathlib.Path
    ) -> None:
        super().__init__(root=root, output=output)
        self._templates = weaving_templates.TemplateRenderer(templates)
        self._markdown = markdown.MarkdownRender()

        self._indexes: list[tuple[pathlib.Path, models.PageFrontmatter, str]] = []
        self._lock = asyncio.Lock()

    def get_output(self, file: pathlib.Path) -> pathlib.Path:
        output = super().get_output(file)
        if output.name == "index.md":
            return output.parent / "index.html"
        return output.parent / output.name.removesuffix(".md") / "index.html"

    async def process(
        self, pages: pathlib.Path
    ) -> AsyncGenerator[pathlib.Path | Exception]:
        async with self._lock:
            coros = []
            for path, _, files in pages.walk():
                coros.extend([self._process_page(path / f) for f in files])

            async for result in asyncio.as_completed(coros):
                try:
                    if p := await result:
                        yield p
                except Exception as ex:
                    yield ex

    async def _process_page(self, file: pathlib.Path) -> pathlib.Path | None:
        page, fm = await markdown.read_markdown(file)

        match fm.type:
            case "default":
                return await self._process_default(file, fm, page)
            case "blog":
                return await self._process_blog(file, fm, page)
            case "blog_index":
                return await self._process_blog_index(file, fm, page)
            case _:
                assert_never(fm.type)

    async def _process_default(
        self, file: pathlib.Path, fm: models.PageFrontmatter, page: str
    ) -> pathlib.Path:
        try:
            content = await self._markdown.render(page)
        except Exception as ex:
            raise errors.WeavingError(
                f"Rendering markdown for {file.relative_to(self.root)} failed: {ex}"
            ) from ex

        ctx = models.TemplateContext(
            content=content,
            frontmatter=fm,
            rendered_at=datetime.datetime.now(datetime.UTC),
            modified_at=get_modified_at(file),
            git_ref=get_git_ref(file),
        )

        try:
            html = await self._templates.render(ctx)
        except Exception as ex:
            raise errors.WeavingError(
                f'Rendering template for "{file.relative_to(self.root)}" failed: Error '
                f'in template "{ctx.frontmatter.template}": {ex}'
            ) from ex

        output = self.get_output(file)

        try:
            output.parent.mkdir(exist_ok=True, parents=True)
            async with aiofile.async_open(output, "w") as f:
                await f.write(html)
        except Exception as ex:
            raise errors.WeavingError(
                f"Writing rendered page {file.relative_to(self.root)} to "
                f"{output.relative_to(self.output)} failed: {ex}"
            ) from ex

        log.logger("markdown").debug(
            f"Rendered {file.relative_to(self.root.parent)} to "
            f"{output.relative_to(self.output.parent)}"
        )

        return output

    async def _process_blog(
        self, file: pathlib.Path, fm: models.PageFrontmatter, page: str
    ) -> pathlib.Path:
        return await self._process_default(file, fm, page)

    async def _process_blog_index(
        self, file: pathlib.Path, fm: models.PageFrontmatter, page: str
    ) -> pathlib.Path:
        pass


def get_modified_at(path: pathlib.Path) -> datetime.datetime:
    """Returns the time the path was last modified."""
    return datetime.datetime.fromtimestamp(path.stat().st_mtime, datetime.UTC)


def get_git_ref(path: pathlib.Path) -> str | None:
    """Return the current `git` ref for the path."""
    for p in path.parents:
        for dir in p.iterdir():
            if dir.is_dir() and dir.name == ".git":
                head = (
                    (p / ".git" / "HEAD")
                    .read_text("utf-8")
                    .strip()
                    .replace("ref: ", "", 1)
                )
                return (p / ".git" / head).read_text("utf-8").strip()

    raise errors.WeavingError(f"Could not find git ref for {path}")
