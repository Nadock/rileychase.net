import asyncio
import datetime
import math
import pathlib
from collections.abc import AsyncGenerator

import aiofile

from weaving import errors, log, markdown, models
from weaving import templates as weaving_templates

from .pipeline import Pipeline


class MarkdownPipeline(Pipeline):
    def __init__(
        self,
        *,
        root: pathlib.Path,
        output: pathlib.Path,
        templates: weaving_templates.TemplateRenderer,
    ) -> None:
        super().__init__(root=root, output=output)
        self.templates = templates
        self.log = log.logger("page")

    def get_output(self, file: pathlib.Path) -> pathlib.Path:
        output = super().get_output(file)
        if file.name == "index.md":
            return output.parent / "index.html"
        return output.parent / file.name.removesuffix(".md") / "index.html"

    async def write_output(
        self, src: pathlib.Path, html: str, output: pathlib.Path | None = None
    ) -> pathlib.Path:
        _output = output or self.get_output(src)
        try:
            _output.parent.mkdir(exist_ok=True, parents=True)
            async with aiofile.async_open(_output, "w") as f:
                await f.write(html)
        except Exception as ex:
            raise errors.WeavingError(
                f"Writing rendered page {src.relative_to(self.root)} to "
                f"{_output.relative_to(self.output)} failed: {ex}"
            ) from ex

        self.log.debug(
            f"Rendered {src.relative_to(self.root.parent)} to "
            f"{_output.relative_to(self.output.parent)}"
        )
        return _output

    async def render_markdown(self, src: pathlib.Path, md: str) -> str:
        try:
            return await markdown.render(md)
        except Exception as ex:
            raise errors.WeavingError(
                f"Rendering markdown for {src.relative_to(self.root)} failed: {ex}"
            ) from ex

    async def render_template(
        self, src: pathlib.Path, ctx: models.TemplateContext
    ) -> str:
        try:
            return await self.templates.render(ctx)
        except Exception as ex:
            raise errors.WeavingError(
                f'Rendering template for "{src.relative_to(self.root)}" failed: Error '
                f'in template "{ctx.frontmatter.template}": {ex}'
            ) from ex

    def process(
        self,
        file: pathlib.Path,
        *,
        page: str | None = None,
        fm: models.PageFrontmatter | None = None,
    ) -> AsyncGenerator[pathlib.Path | Exception]:
        raise NotImplementedError


class DefaultPagePipeline(MarkdownPipeline):
    async def process(
        self,
        file: pathlib.Path,
        *,
        page: str | None = None,
        fm: models.PageFrontmatter | None = None,
    ) -> AsyncGenerator[pathlib.Path | Exception]:
        if not page or not fm:
            page, fm = await markdown.read_markdown(file)

        content = await self.render_markdown(file, page)

        ctx = models.TemplateContext(
            content=content,
            frontmatter=fm,
            rendered_at=datetime.datetime.now(datetime.UTC),
            modified_at=get_modified_at(file),
            git_ref=get_git_ref(file),
        )

        html = await self.render_template(file, ctx)

        yield await self.write_output(file, html)


class BlogIndexPipeline(MarkdownPipeline):
    def __init__(
        self,
        *,
        root: pathlib.Path,
        output: pathlib.Path,
        templates: weaving_templates.TemplateRenderer,
        per_page: int = 5,
    ) -> None:
        super().__init__(root=root, output=output, templates=templates)
        self.per_page = per_page

    async def process(
        self,
        index: pathlib.Path,
        *,
        page: str | None = None,
        fm: models.PageFrontmatter | None = None,
    ) -> AsyncGenerator[pathlib.Path | Exception]:
        if not page or not fm:
            page, fm = await markdown.read_markdown(index)

        blog_root = self.get_output(index).parent

        md, fm = await markdown.read_markdown(index)
        content = await self.render_markdown(index, md)

        posts = await self.find_posts(index)
        max_pages = math.ceil(len(posts) / self.per_page)

        for page_num in range(0, len(posts), self.per_page):
            ctx = models.BlogIndexTemplateContext(
                content=content,
                frontmatter=fm,
                rendered_at=datetime.datetime.now(datetime.UTC),
                modified_at=get_modified_at(index),
                git_ref=get_git_ref(index),
                posts=posts[page_num : page_num + self.per_page],
                current_page=page_num + 1,
                max_pages=max_pages,
            )

            html = await self.render_template(index, ctx)

            yield await self.write_output(
                index, html, blog_root / "_" / str(page_num + 1) / "index.html"
            )

            if page_num == 0:
                yield await self.write_output(index, html, blog_root / "index.html")

    async def find_posts(self, index: pathlib.Path) -> list[models.BlogPostInfo]:
        post_info = []
        for path, _, files in index.parent.walk():
            for file in files:
                p = path / file
                if p != index:
                    post_info.append(self.get_post_info(p))

        return await asyncio.gather(*post_info)

    async def get_post_info(self, path: pathlib.Path) -> models.BlogPostInfo:
        page, fm = await markdown.read_markdown(path)
        preview = await markdown.preview(page)
        return models.BlogPostInfo(
            fm=fm,
            preview=preview or "This page has no paragraphs, please add some content!",
        )


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
