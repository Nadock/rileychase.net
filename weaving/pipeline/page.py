import asyncio
import pathlib
from collections.abc import AsyncGenerator

from weaving import markdown, models
from weaving import templates as weaving_templates

from .page_types import BlogIndexPipeline, DefaultPagePipeline, MarkdownPipeline
from .pipeline import Pipeline


class PagePipeline(Pipeline):
    def __init__(
        self, *, root: pathlib.Path, output: pathlib.Path, templates: pathlib.Path
    ) -> None:
        super().__init__(root=root, output=output)
        self.templates = weaving_templates.TemplateRenderer(templates)

        self.pipelines: dict[models.PageType, MarkdownPipeline] = {
            "default": DefaultPagePipeline(
                root=self.root, output=self.output, templates=self.templates
            ),
            "blog": DefaultPagePipeline(
                root=self.root, output=self.output, templates=self.templates
            ),
            "blog_index": BlogIndexPipeline(
                root=self.root, output=self.output, templates=self.templates
            ),
        }

    async def process(
        self, pages: pathlib.Path
    ) -> AsyncGenerator[pathlib.Path | Exception]:
        coros = []
        for path, _, files in pages.walk():
            coros.extend([self._process_page(path / f) for f in files])

        async for result in asyncio.as_completed(coros):
            try:
                for r in await result:
                    yield r
            except Exception as ex:
                yield ex

    async def _process_page(self, file: pathlib.Path) -> list[pathlib.Path | Exception]:
        page, fm = await markdown.read_markdown(file)
        return [
            r async for r in self.pipelines[fm.type].process(file, page=page, fm=fm)
        ]
