import abc
import asyncio
import datetime
import pathlib
import shutil

import aiofile

from weaving import errors, log, markdown, models
from weaving import templates as weaving_templates


class Pipeline(abc.ABC):
    def __init__(self, *, root: pathlib.Path, output: pathlib.Path) -> None:
        super().__init__()
        self.root = root
        self.output = output

    def get_output(self, file: pathlib.Path) -> pathlib.Path:
        return self.output / (file.relative_to(self.root))

    @abc.abstractmethod
    async def process(self, file: pathlib.Path) -> pathlib.Path: ...


class WeavingPipeline:
    def __init__(
        self,
        *,
        root: pathlib.Path,
        templates: pathlib.Path,
        output: pathlib.Path,
        static: pathlib.Path,
        pages: pathlib.Path,
    ) -> None:
        self._static_pipeline = StaticPipeline(root=root, output=output)
        self._static = static

        self._markdown_pipeline = MarkdownPipeline(
            root=root, output=output, templates=templates
        )
        self._pages = pages

    async def process(self) -> None:
        await asyncio.gather(
            self._process_static(self._static), self._process_pages(self._pages)
        )

    async def _process_pages(self, path: pathlib.Path) -> None:
        if path.is_file():
            await self._markdown_pipeline.process(path)
            return

        await asyncio.gather(*[self._process_pages(p) for p in path.iterdir()])

    async def _process_static(self, path: pathlib.Path) -> None:
        if path.is_file():
            await self._static_pipeline.process(path)
            return

        await asyncio.gather(*[self._process_static(p) for p in path.iterdir()])


class StaticPipeline(Pipeline):
    async def process(self, file: pathlib.Path) -> pathlib.Path:
        output = self.get_output(file)

        try:
            output.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(file, output)
        except Exception as ex:
            raise errors.WeavingError(
                f"Copying static file from {file.relative_to(self.root)} to "
                f"{output.relative_to(self.output)} failed: {ex}"
            ) from ex

        log.logger("static").debug(
            f"Copied {file.relative_to(self.root.parent)} to "
            f"{output.relative_to(self.output.parent)}"
        )

        return output


class MarkdownPipeline(Pipeline):
    def __init__(
        self, *, root: pathlib.Path, output: pathlib.Path, templates: pathlib.Path
    ) -> None:
        super().__init__(root=root, output=output)
        self.templates = weaving_templates.TemplateRenderer(templates)
        self.markdown = markdown.MarkdownRender()

    def get_output(self, file: pathlib.Path) -> pathlib.Path:
        output = super().get_output(file)
        return output.parent / ".md".join(output.name.rsplit(".md", 1))

    async def process(self, file: pathlib.Path) -> pathlib.Path:
        try:
            page, fm = await markdown.read_markdown(file)
        except Exception as ex:
            raise errors.WeavingError(
                f"Reading markdown from {file.relative_to(self.root)} failed: {ex}"
            ) from ex

        try:
            content = await self.markdown.render(page)
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
            html = await self.templates.render(ctx)
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
